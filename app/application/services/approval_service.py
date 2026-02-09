from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.approval_rules import (
    can_transition_approval_status,
    can_transition_document_status,
    can_transition_step_status,
)
from app.domain.enums import ApprovalStatus, ApprovalStepStatus, DocumentStatus
from app.infrastructure.repositories.approval_repository import ApprovalRepository
from app.infrastructure.repositories.document_repository import DocumentRepository
from app.services.base import BaseService


class ApprovalService(BaseService):
    """Service layer for approval workflow."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service with a session."""
        super().__init__(session)
        self.repository = ApprovalRepository(session)
        self.documents = DocumentRepository(session)

    async def create_approval_flow(self, document_id: int, approvers: list[int]):
        """Create approval flow for a document."""
        if not approvers:
            return None
        async with self.session.begin():
            document = await self.documents.get_document(document_id)
            if not document:
                return None
            if document.is_archived:
                return None
            current_status = DocumentStatus(document.status)
            if not can_transition_document_status(current_status, DocumentStatus.APPROVAL):
                return None
            if document.status == DocumentStatus.APPROVAL.value:
                approval = await self.repository.get_by_document_id(document_id)
                if approval:
                    return approval
            approval = await self.repository.create_approval(
                document_id=document.id,
                status=ApprovalStatus.PENDING.value,
            )
            for approver_id in approvers:
                await self.repository.create_step(
                    approval_id=approval.id,
                    approver_id=approver_id,
                    status=ApprovalStepStatus.PENDING.value,
                )
            document.status = DocumentStatus.APPROVAL.value
            return approval

    async def approve_step(self, step_id: int, user_id: int):
        """Approve a single step."""
        async with self.session.begin():
            step = await self.repository.get_step(step_id)
            if not step:
                return None
            if step.approver_id != user_id:
                return None
            current_status = ApprovalStepStatus(step.status)
            if not can_transition_step_status(current_status, ApprovalStepStatus.APPROVED):
                return None
            step.status = ApprovalStepStatus.APPROVED.value
            step.rejection_reason = None
            await self.recalc_approval_status(step.approval_id)
            return step

    async def reject_step(self, step_id: int, user_id: int, reason: str):
        """Reject a single step with reason and cancel the document."""
        return await self._reject_step(step_id, user_id, reason, DocumentStatus.CANCELED)

    async def request_revision_step(self, step_id: int, user_id: int, reason: str):
        """Reject a step and request revision."""
        return await self._reject_step(step_id, user_id, reason, DocumentStatus.REVISION_REQUIRED)

    async def _reject_step(
        self,
        step_id: int,
        user_id: int,
        reason: str,
        document_target: DocumentStatus,
    ):
        """Reject a single step with reason and update document status."""
        if not reason:
            return None
        async with self.session.begin():
            step = await self.repository.get_step(step_id)
            if not step:
                return None
            if step.approver_id != user_id:
                return None
            current_status = ApprovalStepStatus(step.status)
            if not can_transition_step_status(current_status, ApprovalStepStatus.REJECTED):
                return None
            step.status = ApprovalStepStatus.REJECTED.value
            step.rejection_reason = reason
            approval = step.approval or await self.repository.get_approval(step.approval_id)
            if not approval:
                return step
            approval_status = ApprovalStatus(approval.status)
            if can_transition_approval_status(approval_status, ApprovalStatus.REJECTED):
                approval.status = ApprovalStatus.REJECTED.value
            document = await self.documents.get_document(approval.document_id)
            if not document or document.is_archived:
                return step
            document_status = DocumentStatus(document.status)
            if (
                document_target.value != document.status
                and can_transition_document_status(document_status, document_target)
            ):
                document.status = document_target.value
            return step

    async def recalc_approval_status(self, approval_id: int):
        """Recalculate approval status based on steps."""
        approval = await self.repository.get_approval(approval_id)
        if not approval:
            return None
        document = await self.documents.get_document(approval.document_id)
        if not document:
            return None
        if document.status == DocumentStatus.CANCELED.value:
            return approval
        steps = approval.steps
        if any(step.status == ApprovalStepStatus.REJECTED.value for step in steps):
            target_status = ApprovalStatus.REJECTED
            document_target = DocumentStatus.REVISION_REQUIRED
        elif steps and all(step.status == ApprovalStepStatus.APPROVED.value for step in steps):
            target_status = ApprovalStatus.APPROVED
            document_target = DocumentStatus.APPROVED
        else:
            target_status = ApprovalStatus.PENDING
            document_target = DocumentStatus.APPROVAL
        if (
            target_status.value != approval.status
            and can_transition_approval_status(ApprovalStatus(approval.status), target_status)
        ):
            approval.status = target_status.value
        document_status = DocumentStatus(document.status)
        if (
            document_target.value != document.status
            and can_transition_document_status(document_status, document_target)
        ):
            document.status = document_target.value
        return approval

    async def get_approval_with_steps(self, document_id: int):
        """Get approval and steps for a document."""
        approval = await self.repository.get_by_document_id(document_id)
        if not approval:
            return None, []
        steps = approval.steps
        return approval, steps

    async def list_pending_documents(self, approver_id: int):
        """List documents awaiting approver action."""
        return await self.repository.list_documents_for_approver(approver_id)

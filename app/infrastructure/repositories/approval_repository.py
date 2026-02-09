from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models.approval import Approval, ApprovalStep
from app.repositories.base import BaseRepository


class ApprovalRepository(BaseRepository):
    """Repository for approval persistence."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with a session."""
        super().__init__(session)

    async def get_approval(self, approval_id: int) -> Approval | None:
        """Fetch approval by identifier."""
        try:
            result = await self.session.execute(
                select(Approval)
                .options(selectinload(Approval.steps))
                .where(Approval.id == approval_id)
            )
            return result.scalars().first()
        except SQLAlchemyError:
            self.logger.exception("Failed to fetch approval", extra={"approval_id": approval_id})
            raise

    async def get_by_document_id(self, document_id: int) -> Approval | None:
        """Fetch approval by document identifier."""
        try:
            result = await self.session.execute(
                select(Approval)
                .options(selectinload(Approval.steps))
                .where(Approval.document_id == document_id)
                .order_by(Approval.id.desc())
            )
            return result.scalars().first()
        except SQLAlchemyError:
            self.logger.exception("Failed to fetch approval", extra={"document_id": document_id})
            raise

    async def create_approval(self, document_id: int, status: str) -> Approval:
        """Create and persist approval."""
        approval = Approval(document_id=document_id, status=status)
        self.session.add(approval)
        try:
            await self.session.flush()
            await self.session.refresh(approval)
            return approval
        except SQLAlchemyError:
            self.logger.exception("Failed to create approval", extra={"document_id": document_id})
            raise

    async def create_step(self, approval_id: int, approver_id: int, status: str) -> ApprovalStep:
        """Create and persist approval step."""
        step = ApprovalStep(approval_id=approval_id, approver_id=approver_id, status=status)
        self.session.add(step)
        try:
            await self.session.flush()
            await self.session.refresh(step)
            return step
        except SQLAlchemyError:
            self.logger.exception(
                "Failed to create approval step",
                extra={"approval_id": approval_id, "approver_id": approver_id},
            )
            raise

    async def get_step(self, step_id: int) -> ApprovalStep | None:
        """Fetch approval step by identifier."""
        try:
            result = await self.session.execute(
                select(ApprovalStep)
                .options(selectinload(ApprovalStep.approval))
                .where(ApprovalStep.id == step_id)
            )
            return result.scalars().first()
        except SQLAlchemyError:
            self.logger.exception("Failed to fetch approval step", extra={"step_id": step_id})
            raise

    async def list_steps(self, approval_id: int) -> list[ApprovalStep]:
        """List steps for approval."""
        try:
            result = await self.session.execute(
                select(ApprovalStep)
                .where(ApprovalStep.approval_id == approval_id)
                .order_by(ApprovalStep.id.asc())
            )
            return list(result.scalars().all())
        except SQLAlchemyError:
            self.logger.exception("Failed to list approval steps", extra={"approval_id": approval_id})
            raise

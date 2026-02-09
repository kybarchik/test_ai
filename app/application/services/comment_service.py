from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.repositories.approval_repository import ApprovalRepository
from app.infrastructure.repositories.comment_repository import CommentRepository
from app.infrastructure.repositories.document_repository import DocumentRepository
from app.services.base import BaseService


class CommentService(BaseService):
    """Service layer for comment operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service with a session."""
        super().__init__(session)
        self.comments = CommentRepository(session)
        self.documents = DocumentRepository(session)
        self.approvals = ApprovalRepository(session)

    async def add_comment(
        self,
        content: str,
        document_id: int | None,
        approval_id: int | None,
    ):
        """Add a comment to a document or approval."""
        if not content:
            return None
        if bool(document_id) == bool(approval_id):
            return None
        async with self.session.begin():
            if document_id:
                document = await self.documents.get_document(document_id)
                if not document or document.is_archived:
                    return None
            if approval_id:
                approval = await self.approvals.get_approval(approval_id)
                if not approval:
                    return None
            return await self.comments.create_comment(
                content=content,
                document_id=document_id,
                approval_id=approval_id,
            )

    async def list_for_document(self, document_id: int):
        """List comments for a document."""
        return await self.comments.list_for_document(document_id)

    async def list_for_approval(self, approval_id: int):
        """List comments for an approval."""
        return await self.comments.list_for_approval(approval_id)

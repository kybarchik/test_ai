from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.comment import Comment
from app.repositories.base import BaseRepository


class CommentRepository(BaseRepository):
    """Repository for managing comments."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with a session."""
        super().__init__(session)

    async def create_comment(
        self,
        content: str,
        document_id: int | None,
        approval_id: int | None,
    ) -> Comment:
        """Create a new comment."""
        comment = Comment(content=content, document_id=document_id, approval_id=approval_id)
        self.session.add(comment)
        await self.session.flush()
        return comment

    async def list_for_document(self, document_id: int) -> list[Comment]:
        """List comments for a document."""
        result = await self.session.execute(
            select(Comment)
            .where(Comment.document_id == document_id)
            .order_by(Comment.created_at.asc())
        )
        return list(result.scalars().all())

    async def list_for_approval(self, approval_id: int) -> list[Comment]:
        """List comments for an approval."""
        result = await self.session.execute(
            select(Comment)
            .where(Comment.approval_id == approval_id)
            .order_by(Comment.created_at.asc())
        )
        return list(result.scalars().all())

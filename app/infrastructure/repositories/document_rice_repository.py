from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.document_rice import DocumentRICE
from app.repositories.base import BaseRepository


class DocumentRICERepository(BaseRepository):
    """Repository for managing document RICE scores."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with a session."""
        super().__init__(session)

    async def create_rice(
        self,
        document_id: int,
        author_id: int,
        reach: float,
        impact: float,
        confidence: float,
        effort: float,
        score: float,
    ) -> DocumentRICE:
        """Create a new RICE score for a document."""
        rice = DocumentRICE(
            document_id=document_id,
            author_id=author_id,
            reach=reach,
            impact=impact,
            confidence=confidence,
            effort=effort,
            score=score,
        )
        self.session.add(rice)
        await self.session.flush()
        return rice

    async def get_rice(self, rice_id: int) -> DocumentRICE | None:
        """Get a RICE score by id."""
        result = await self.session.execute(select(DocumentRICE).where(DocumentRICE.id == rice_id))
        return result.scalar_one_or_none()

    async def update_rice(
        self,
        rice: DocumentRICE,
        reach: float,
        impact: float,
        confidence: float,
        effort: float,
        score: float,
    ) -> DocumentRICE:
        """Update an existing RICE score."""
        rice.reach = reach
        rice.impact = impact
        rice.confidence = confidence
        rice.effort = effort
        rice.score = score
        await self.session.flush()
        return rice

    async def list_for_document(self, document_id: int) -> list[DocumentRICE]:
        """List RICE scores for a document."""
        result = await self.session.execute(
            select(DocumentRICE)
            .where(DocumentRICE.document_id == document_id)
            .order_by(DocumentRICE.id.asc())
        )
        return list(result.scalars().all())

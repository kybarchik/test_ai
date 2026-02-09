from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import DocumentStatus
from app.domain.models.document_rice import DocumentRICE
from app.infrastructure.repositories.document_repository import DocumentRepository
from app.infrastructure.repositories.document_rice_repository import DocumentRICERepository
from app.services.base import BaseService


class DocumentRICEService(BaseService):
    """Service layer for document RICE scores."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service with a session."""
        super().__init__(session)
        self.documents = DocumentRepository(session)
        self.rices = DocumentRICERepository(session)

    async def add_rice(self, document_id: int, author_id: int, data: dict) -> DocumentRICE | None:
        """Add a RICE score to a document."""
        reach = data.get("reach")
        impact = data.get("impact")
        confidence = data.get("confidence")
        effort = data.get("effort")
        if reach is None or impact is None or confidence is None or effort is None:
            return None
        async with self.session.begin():
            document = await self.documents.get_document(document_id)
            if not document or document.is_archived:
                return None
            if document.status != DocumentStatus.APPROVAL.value:
                return None
            score = self.calc_score(reach, impact, confidence, effort)
            return await self.rices.create_rice(
                document_id=document_id,
                author_id=author_id,
                reach=reach,
                impact=impact,
                confidence=confidence,
                effort=effort,
                score=score,
            )

    async def update_rice(self, rice_id: int, author_id: int, data: dict) -> DocumentRICE | None:
        """Update a RICE score for a document."""
        reach = data.get("reach")
        impact = data.get("impact")
        confidence = data.get("confidence")
        effort = data.get("effort")
        if reach is None or impact is None or confidence is None or effort is None:
            return None
        async with self.session.begin():
            rice = await self.rices.get_rice(rice_id)
            if not rice:
                return None
            if rice.author_id != author_id:
                return None
            document = await self.documents.get_document(rice.document_id)
            if not document or document.is_archived:
                return None
            if document.status != DocumentStatus.APPROVAL.value:
                return None
            score = self.calc_score(reach, impact, confidence, effort)
            return await self.rices.update_rice(
                rice=rice,
                reach=reach,
                impact=impact,
                confidence=confidence,
                effort=effort,
                score=score,
            )

    async def list_rice_for_document(self, document_id: int) -> list[DocumentRICE]:
        """List RICE scores for a document."""
        return await self.rices.list_for_document(document_id)

    def calc_score(self, reach: float, impact: float, confidence: float, effort: float) -> float:
        """Calculate RICE score."""
        if effort <= 0:
            return 0.0
        return (reach * impact * confidence) / effort

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import DocumentStatus
from app.infrastructure.repositories.document_metric_repository import DocumentMetricRepository
from app.infrastructure.repositories.document_repository import DocumentRepository
from app.services.base import BaseService


class DocumentMetricService(BaseService):
    """Service layer for document metrics."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service with a session."""
        super().__init__(session)
        self.documents = DocumentRepository(session)
        self.metrics = DocumentMetricRepository(session)

    async def add_metric(self, document_id: int, name: str, value: str, unit: str):
        """Add a metric to a document."""
        if not name or not value or not unit:
            return None
        async with self.session.begin():
            document = await self.documents.get_document(document_id)
            if not document or document.is_archived:
                return None
            if document.status == DocumentStatus.APPROVED.value:
                return None
            return await self.metrics.create_metric(document_id=document_id, name=name, value=value, unit=unit)

    async def update_metric(self, document_id: int, metric_id: int, name: str, value: str, unit: str):
        """Update a metric in a document."""
        if not name or not value or not unit:
            return None
        async with self.session.begin():
            document = await self.documents.get_document(document_id)
            if not document or document.is_archived:
                return None
            if document.status == DocumentStatus.APPROVED.value:
                return None
            metric = await self.metrics.get_metric(metric_id)
            if not metric or metric.document_id != document_id:
                return None
            return await self.metrics.update_metric(metric, name=name, value=value, unit=unit)

    async def delete_metric(self, document_id: int, metric_id: int) -> bool:
        """Delete a metric from a document."""
        async with self.session.begin():
            document = await self.documents.get_document(document_id)
            if not document or document.is_archived:
                return False
            if document.status == DocumentStatus.APPROVED.value:
                return False
            metric = await self.metrics.get_metric(metric_id)
            if not metric or metric.document_id != document_id:
                return False
            await self.metrics.delete_metric(metric)
            return True

    async def list_metrics_for_document(self, document_id: int):
        """List metrics for a document."""
        return await self.metrics.list_for_document(document_id)

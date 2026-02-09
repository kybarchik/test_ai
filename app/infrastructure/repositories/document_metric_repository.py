from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.document_metric import DocumentMetric
from app.repositories.base import BaseRepository


class DocumentMetricRepository(BaseRepository):
    """Repository for managing document metrics."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with a session."""
        super().__init__(session)

    async def create_metric(self, document_id: int, name: str, value: str, unit: str) -> DocumentMetric:
        """Create a new metric for a document."""
        metric = DocumentMetric(document_id=document_id, name=name, value=value, unit=unit)
        self.session.add(metric)
        await self.session.flush()
        return metric

    async def get_metric(self, metric_id: int) -> DocumentMetric | None:
        """Get a metric by id."""
        result = await self.session.execute(select(DocumentMetric).where(DocumentMetric.id == metric_id))
        return result.scalar_one_or_none()

    async def update_metric(self, metric: DocumentMetric, name: str, value: str, unit: str) -> DocumentMetric:
        """Update an existing metric."""
        metric.name = name
        metric.value = value
        metric.unit = unit
        await self.session.flush()
        return metric

    async def delete_metric(self, metric: DocumentMetric) -> None:
        """Delete a metric."""
        await self.session.delete(metric)
        await self.session.flush()

    async def list_for_document(self, document_id: int) -> list[DocumentMetric]:
        """List metrics for a document."""
        result = await self.session.execute(
            select(DocumentMetric)
            .where(DocumentMetric.document_id == document_id)
            .order_by(DocumentMetric.id.asc())
        )
        return list(result.scalars().all())

import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import Pagination
from app.models.record import Record


class RecordRepository:
    """Repository for record database operations."""

    logger = logging.getLogger(__name__)

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with an async session."""
        self.session = session

    async def list_records(self, pagination: Pagination) -> list[Record]:
        """List records using pagination."""
        try:
            result = await self.session.execute(
                select(Record).order_by(Record.id.desc()).offset(pagination.offset).limit(pagination.size)
            )
            return list(result.scalars().all())
        except SQLAlchemyError:
            self.logger.exception("Failed to list records")
            raise

    async def get_record(self, record_id: int) -> Record | None:
        """Fetch a record by id."""
        try:
            result = await self.session.execute(select(Record).where(Record.id == record_id))
            return result.scalars().first()
        except SQLAlchemyError:
            self.logger.exception("Failed to fetch record", extra={"record_id": record_id})
            raise

    async def create_record(self, title: str, description: str | None) -> Record:
        """Create and persist a new record."""
        record = Record(title=title, description=description, created_at=datetime.now(timezone.utc))
        self.session.add(record)
        try:
            await self.session.flush()
            await self.session.refresh(record)
            return record
        except SQLAlchemyError:
            self.logger.exception("Failed to create record")
            raise

    async def update_record(self, record: Record, title: str, description: str | None) -> Record:
        """Update an existing record."""
        record.title = title
        record.description = description
        try:
            await self.session.flush()
            await self.session.refresh(record)
            return record
        except SQLAlchemyError:
            self.logger.exception("Failed to update record", extra={"record_id": record.id})
            raise

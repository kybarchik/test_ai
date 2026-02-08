from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.records.model import Record
from app.repositories.base import BaseRepository


class RecordRepository(BaseRepository):
    """Repository for record database operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with a session."""
        super().__init__(session)

    async def list_records(self, offset: int, limit: int) -> list[Record]:
        """Return a page of records."""
        try:
            result = await self.session.execute(
                select(Record).order_by(Record.created_at.desc()).offset(offset).limit(limit)
            )
            return list(result.scalars().all())
        except SQLAlchemyError:
            self.logger.exception("Failed to list records", extra={"offset": offset, "limit": limit})
            raise

    async def count_records(self) -> int:
        """Return total number of records."""
        try:
            result = await self.session.execute(select(func.count()).select_from(Record))
            return int(result.scalar_one())
        except SQLAlchemyError:
            self.logger.exception("Failed to count records")
            raise

    async def get_record(self, record_id: int) -> Record | None:
        """Return a record by ID."""
        try:
            result = await self.session.execute(select(Record).where(Record.id == record_id))
            return result.scalars().first()
        except SQLAlchemyError:
            self.logger.exception("Failed to fetch record", extra={"record_id": record_id})
            raise

    async def create_record(self, title: str, description: str | None) -> Record:
        """Create a new record."""
        record = Record(title=title, description=description)
        self.session.add(record)
        try:
            await self.session.flush()
            await self.session.refresh(record)
            return record
        except SQLAlchemyError:
            self.logger.exception("Failed to create record", extra={"title": title})
            raise

    async def update_record(self, record: Record, title: str, description: str | None) -> Record:
        """Update a record."""
        record.title = title
        record.description = description
        try:
            await self.session.flush()
            await self.session.refresh(record)
            return record
        except SQLAlchemyError:
            self.logger.exception("Failed to update record", extra={"record_id": record.id})
            raise

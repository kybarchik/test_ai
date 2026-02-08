from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.records.repository import RecordRepository
from app.schemas.record import RecordCreate, RecordUpdate
from app.services.base import BaseService


class RecordService(BaseService):
    """Service layer for record workflows."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service with a session."""
        super().__init__(session)
        self.repository = RecordRepository(session)

    async def list_records(self, offset: int, limit: int):
        """Return list of records and total count."""
        records = await self.repository.list_records(offset=offset, limit=limit)
        total = await self.repository.count_records()
        return records, total

    async def get_record(self, record_id: int):
        """Get a record or None."""
        return await self.repository.get_record(record_id=record_id)

    async def create_record(self, payload: RecordCreate):
        """Create a new record."""
        return await self.repository.create_record(title=payload.title, description=payload.description)

    async def update_record(self, record_id: int, payload: RecordUpdate):
        """Update an existing record."""
        record = await self.repository.get_record(record_id=record_id)
        if not record:
            return None
        return await self.repository.update_record(record, title=payload.title, description=payload.description)

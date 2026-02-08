from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import Pagination
from app.repositories.record_repository import RecordRepository
from app.schemas.record import RecordCreate, RecordUpdate


class RecordService:
    """Service for record workflows."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the service with an async session."""
        self.session = session
        self.repository = RecordRepository(session)

    async def list_records(self, pagination: Pagination):
        """Return a list of records."""
        return await self.repository.list_records(pagination)

    async def get_record(self, record_id: int):
        """Return a single record by id."""
        return await self.repository.get_record(record_id)

    async def create_record(self, payload: RecordCreate):
        """Create a new record."""
        async with self.session.begin():
            return await self.repository.create_record(title=payload.title, description=payload.description)

    async def update_record(self, record_id: int, payload: RecordUpdate):
        """Update an existing record."""
        record = await self.repository.get_record(record_id)
        if not record:
            return None
        async with self.session.begin():
            return await self.repository.update_record(record, title=payload.title, description=payload.description)

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.items.tasks.test_module.repository import TestModuleRepository
from app.services.base import BaseService


class TestModuleService(BaseService):
    """Service for the example module."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service with a session."""
        super().__init__(session)
        self.repository = TestModuleRepository(session)

    async def list_items(self):
        """List items in the example module."""
        return await self.repository.list_items()

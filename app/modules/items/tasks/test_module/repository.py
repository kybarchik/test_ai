from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.items.tasks.test_module.model import TestModuleItem
from app.repositories.base import BaseRepository


class TestModuleRepository(BaseRepository):
    """Repository for the example module."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with a session."""
        super().__init__(session)

    async def list_items(self) -> list[TestModuleItem]:
        """List example module items."""
        try:
            result = await self.session.execute(select(TestModuleItem))
            return list(result.scalars().all())
        except SQLAlchemyError:
            self.logger.exception("Failed to list test module items")
            raise

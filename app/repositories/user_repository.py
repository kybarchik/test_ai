import logging

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    """Repository for user database operations."""

    logger = logging.getLogger(__name__)

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with an async session."""
        self.session = session

    async def get_by_username(self, username: str) -> User | None:
        """Fetch a user by username."""
        try:
            result = await self.session.execute(select(User).where(User.username == username))
            return result.scalars().first()
        except SQLAlchemyError:
            self.logger.exception("Failed to fetch user", extra={"username": username})
            raise

    async def create_user(self, username: str, hashed_password: str) -> User:
        """Create and persist a new user."""
        user = User(username=username, hashed_password=hashed_password)
        self.session.add(user)
        try:
            await self.session.flush()
            await self.session.refresh(user)
            return user
        except SQLAlchemyError:
            self.logger.exception("Failed to create user", extra={"username": username})
            raise

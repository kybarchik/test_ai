from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    """Repository for user database operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with a session."""
        super().__init__(session)

    async def get_by_email(self, email: str) -> User | None:
        """Fetch a user by email."""
        try:
            result = await self.session.execute(select(User).where(User.email == email))
            return result.scalars().first()
        except SQLAlchemyError:
            self.logger.exception("Failed to fetch user", extra={"email": email})
            raise

    async def create_user(self, email: str, full_name: str, password_hash: str) -> User:
        """Create and persist a new user."""
        user = User(email=email, full_name=full_name, password_hash=password_hash, is_active=True)
        self.session.add(user)
        try:
            await self.session.flush()
            await self.session.refresh(user)
            return user
        except SQLAlchemyError:
            self.logger.exception("Failed to create user", extra={"email": email})
            raise

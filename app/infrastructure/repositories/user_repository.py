from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    """Repository for user persistence."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with a session."""
        super().__init__(session)

    async def get_by_id(self, user_id: int) -> User | None:
        """Fetch a user by identifier."""
        try:
            result = await self.session.execute(select(User).where(User.id == user_id))
            return result.scalars().first()
        except SQLAlchemyError:
            self.logger.exception("Failed to fetch user by id", extra={"user_id": user_id})
            raise

    async def get_by_email(self, email: str) -> User | None:
        """Fetch a user by email."""
        try:
            result = await self.session.execute(select(User).where(User.email == email))
            return result.scalars().first()
        except SQLAlchemyError:
            self.logger.exception("Failed to fetch user by email", extra={"email": email})
            raise

    async def create(self, email: str, full_name: str, password_hash: str) -> User:
        """Create and persist a user."""
        user = User(email=email, full_name=full_name, password_hash=password_hash, is_active=True)
        self.session.add(user)
        try:
            await self.session.flush()
            await self.session.refresh(user)
            return user
        except SQLAlchemyError:
            self.logger.exception("Failed to create user", extra={"email": email})
            raise

    async def update(
        self,
        user: User,
        email: str | None,
        full_name: str | None,
        password_hash: str | None,
    ) -> User:
        """Update an existing user."""
        if email is not None:
            user.email = email
        if full_name is not None:
            user.full_name = full_name
        if password_hash is not None:
            user.password_hash = password_hash
        try:
            await self.session.flush()
            await self.session.refresh(user)
            return user
        except SQLAlchemyError:
            self.logger.exception("Failed to update user", extra={"user_id": user.id})
            raise

    async def deactivate(self, user: User) -> User:
        """Deactivate a user."""
        user.is_active = False
        try:
            await self.session.flush()
            await self.session.refresh(user)
            return user
        except SQLAlchemyError:
            self.logger.exception("Failed to deactivate user", extra={"user_id": user.id})
            raise

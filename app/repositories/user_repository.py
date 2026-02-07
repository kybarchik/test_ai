from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    """Repository for user database operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with an async session."""
        self.session = session

    async def get_by_username(self, username: str) -> User | None:
        """Fetch a user by username."""
        result = await self.session.execute(select(User).where(User.username == username))
        return result.scalars().first()

    async def create_user(self, username: str, hashed_password: str) -> User:
        """Create and persist a new user."""
        user = User(username=username, hashed_password=hashed_password)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

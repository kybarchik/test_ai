from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.repositories.user_repository import UserRepository


class AuthService:
    """Service for authentication workflows."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the service with an async session."""
        self.session = session
        self.repository = UserRepository(session)

    async def authenticate(self, username: str, password: str) -> bool:
        """Validate user credentials."""
        user = await self.repository.get_by_username(username)
        if not user:
            return False
        return verify_password(password, user.hashed_password)

    async def register(self, username: str, password: str) -> None:
        """Register a new user with a hashed password."""
        hashed_password = get_password_hash(password)
        async with self.session.begin():
            await self.repository.create_user(username=username, hashed_password=hashed_password)

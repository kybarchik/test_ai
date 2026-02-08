from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.repositories.user_repository import UserRepository
from app.services.base import BaseService


class AuthService(BaseService):
    """Service for authentication workflows."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the service with an async session."""
        super().__init__(session)
        self.repository = UserRepository(session)

    async def authenticate(self, email: str, password: str) -> bool:
        """Validate user credentials."""
        user = await self.repository.get_by_email(email)
        if not user:
            return False
        if not user.is_active:
            return False
        return verify_password(password, user.password_hash)

    async def register(self, email: str, full_name: str, password: str) -> None:
        """Register a new user with a hashed password."""
        password_hash = get_password_hash(password)
        await self.repository.create_user(email=email, full_name=full_name, password_hash=password_hash)

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.infrastructure.repositories.user_repository import UserRepository
from app.services.base import BaseService


class UserService(BaseService):
    """Service layer for user workflows."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service with a session."""
        super().__init__(session)
        self.repository = UserRepository(session)

    async def register_user(self, email: str, full_name: str, password: str):
        """Register a new user."""
        async with self.session.begin():
            existing = await self.repository.get_by_email(email)
            if existing:
                return None
            password_hash = get_password_hash(password)
            return await self.repository.create(email=email, full_name=full_name, password_hash=password_hash)

    async def authenticate_user(self, email: str, password: str):
        """Authenticate a user by email and password."""
        user = await self.repository.get_by_email(email)
        if not user:
            return None
        if not user.is_active:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    async def get_profile(self, user_id: int):
        """Get a user profile by id."""
        return await self.repository.get_by_id(user_id)

    async def update_user(
        self,
        user_id: int,
        email: str | None,
        full_name: str | None,
        password: str | None,
    ):
        """Update an existing user."""
        async with self.session.begin():
            user = await self.repository.get_by_id(user_id)
            if not user:
                return None
            password_hash = get_password_hash(password) if password is not None else None
            return await self.repository.update(
                user=user,
                email=email,
                full_name=full_name,
                password_hash=password_hash,
            )

    async def deactivate_user(self, user_id: int):
        """Deactivate an existing user."""
        async with self.session.begin():
            user = await self.repository.get_by_id(user_id)
            if not user:
                return None
            return await self.repository.deactivate(user)

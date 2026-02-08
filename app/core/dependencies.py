from typing import AsyncGenerator

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import session_scope
from app.repositories.user_repository import UserRepository
from app.core.security import decode_access_token


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide an async database session dependency."""
    async with session_scope() as session:
        yield session


async def get_current_user(
    access_token: str | None = Cookie(default=None),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Resolve the current user from the access token cookie."""
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    subject = decode_access_token(access_token)
    if not subject:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    repository = UserRepository(session)
    user = await repository.get_by_username(subject)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return {"id": user.id, "username": user.username}

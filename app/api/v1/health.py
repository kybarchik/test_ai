from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    """Return basic service health information."""
    return {"status": "ok"}


@router.get("/ready")
async def ready(session: AsyncSession = Depends(get_db_session)) -> dict:
    """Check database readiness."""
    await session.execute(text("SELECT 1"))
    return {"status": "ready"}

from sqlalchemy.ext.asyncio import AsyncSession


class BaseService:
    """Base class for services."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service with a session."""
        self.session = session

import logging

from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    """Base class for repositories."""

    logger = logging.getLogger(__name__)

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with a session."""
        self.session = session

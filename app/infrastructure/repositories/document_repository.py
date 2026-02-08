from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.document import Document
from app.repositories.base import BaseRepository


class DocumentRepository(BaseRepository):
    """Repository for document persistence."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with a session."""
        super().__init__(session)

    async def list_documents(self) -> list[Document]:
        """Return all active documents."""
        try:
            result = await self.session.execute(
                select(Document)
                .where(Document.is_archived.is_(False))
                .order_by(Document.created_at.desc())
            )
            return list(result.scalars().all())
        except SQLAlchemyError:
            self.logger.exception("Failed to list documents")
            raise

    async def get_document(self, document_id: int) -> Document | None:
        """Fetch a document by identifier."""
        try:
            result = await self.session.execute(select(Document).where(Document.id == document_id))
            return result.scalars().first()
        except SQLAlchemyError:
            self.logger.exception("Failed to fetch document", extra={"document_id": document_id})
            raise

    async def create_document(self, title: str, description: str | None) -> Document:
        """Create and persist a document."""
        document = Document(title=title, description=description)
        self.session.add(document)
        try:
            await self.session.flush()
            await self.session.refresh(document)
            return document
        except SQLAlchemyError:
            self.logger.exception("Failed to create document", extra={"title": title})
            raise

    async def update_document(self, document: Document, title: str, description: str | None) -> Document:
        """Update an existing document."""
        document.title = title
        document.description = description
        try:
            await self.session.flush()
            await self.session.refresh(document)
            return document
        except SQLAlchemyError:
            self.logger.exception("Failed to update document", extra={"document_id": document.id})
            raise

    async def archive_document(self, document: Document) -> Document:
        """Archive an existing document."""
        document.is_archived = True
        try:
            await self.session.flush()
            await self.session.refresh(document)
            return document
        except SQLAlchemyError:
            self.logger.exception("Failed to archive document", extra={"document_id": document.id})
            raise

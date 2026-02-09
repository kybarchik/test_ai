from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.approval_rules import can_transition_document_status
from app.domain.enums import DocumentStatus
from app.infrastructure.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentCreate, DocumentUpdate
from app.services.base import BaseService


class DocumentService(BaseService):
    """Service layer for document workflows."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service with a session."""
        super().__init__(session)
        self.repository = DocumentRepository(session)

    async def create_draft(self, payload: DocumentCreate):
        """Create a document draft."""
        async with self.session.begin():
            document = await self.repository.create_document(
                title=payload.title,
                description=payload.description,
            )
            document.status = DocumentStatus.DRAFT.value
            return document

    async def update_draft(self, document_id: int, payload: DocumentUpdate):
        """Update an existing document draft."""
        async with self.session.begin():
            document = await self.repository.get_document(document_id=document_id)
            if not document:
                return None
            if document.is_archived:
                return None
            if document.status not in {
                DocumentStatus.DRAFT.value,
                DocumentStatus.REVISION_REQUIRED.value,
            }:
                return None
            return await self.repository.update_document(
                document=document,
                title=payload.title,
                description=payload.description,
            )

    async def get_document(self, document_id: int):
        """Get a document by identifier."""
        document = await self.repository.get_document(document_id=document_id)
        if not document:
            return None
        if document.is_archived:
            return None
        return document

    async def list_documents(self):
        """List all active documents."""
        return await self.repository.list_documents()

    async def archive_document(self, document_id: int):
        """Archive a document draft."""
        async with self.session.begin():
            document = await self.repository.get_document(document_id=document_id)
            if not document:
                return None
            if document.is_archived:
                return document
            return await self.repository.archive_document(document)

    async def restore_from_canceled(self, document_id: int):
        """Restore a canceled document back to draft."""
        async with self.session.begin():
            document = await self.repository.get_document(document_id=document_id)
            if not document:
                return None
            if document.is_archived:
                return None
            if document.status != DocumentStatus.CANCELED.value:
                return None
            current_status = DocumentStatus(document.status)
            if not can_transition_document_status(current_status, DocumentStatus.DRAFT):
                return None
            document.status = DocumentStatus.DRAFT.value
            return document

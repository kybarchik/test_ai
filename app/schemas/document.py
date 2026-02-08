from datetime import datetime

from pydantic import BaseModel, Field


class DocumentBase(BaseModel):
    """Shared attributes for documents."""

    title: str = Field(..., max_length=255)
    description: str | None = None


class DocumentCreate(DocumentBase):
    """Schema for creating documents."""


class DocumentUpdate(DocumentBase):
    """Schema for updating documents."""


class DocumentRead(DocumentBase):
    """Schema for reading documents."""

    id: int
    status: str
    created_at: datetime
    updated_at: datetime

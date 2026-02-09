from datetime import datetime

from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    """Schema for creating comments."""

    content: str = Field(..., min_length=1)
    document_id: int | None = None
    approval_id: int | None = None


class CommentRead(BaseModel):
    """Schema for reading comments."""

    id: int
    content: str
    document_id: int | None = None
    approval_id: int | None = None
    created_at: datetime

from datetime import datetime

from pydantic import BaseModel, Field


class RecordBase(BaseModel):
    """Shared attributes for records."""

    title: str = Field(..., max_length=255)
    description: str | None = None


class RecordCreate(RecordBase):
    """Schema for creating records."""


class RecordUpdate(RecordBase):
    """Schema for updating records."""


class RecordRead(RecordBase):
    """Schema for reading records."""

    id: int
    created_at: datetime

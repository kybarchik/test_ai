from datetime import datetime

from app.schemas.base import BaseSchema


class RecordCreate(BaseSchema):
    """Schema for record creation."""

    title: str
    description: str | None = None


class RecordUpdate(BaseSchema):
    """Schema for record updates."""

    title: str
    description: str | None = None


class RecordRead(BaseSchema):
    """Schema for record reads."""

    id: int
    title: str
    description: str | None = None
    created_at: datetime

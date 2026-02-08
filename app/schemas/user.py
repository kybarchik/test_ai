from app.schemas.base import BaseSchema


class UserLogin(BaseSchema):
    """Schema for user login."""

    username: str
    password: str

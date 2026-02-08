from pydantic import BaseModel


class UserLogin(BaseModel):
    """Schema for user login."""

    username: str
    password: str

import json
from dataclasses import dataclass
from typing import Any

from fastapi import Request
from fastapi.responses import Response

FLASH_COOKIE_NAME = "flash_message"


@dataclass(slots=True)
class FlashMessage:
    """Representation of a flash message for templates."""

    message: str
    level: str = "info"


def set_flash(response: Response, message: str, level: str = "info") -> None:
    """Store a flash message in a cookie for the next request."""
    payload = json.dumps({"message": message, "level": level})
    response.set_cookie(
        FLASH_COOKIE_NAME,
        payload,
        max_age=10,
        httponly=True,
        samesite="lax",
    )


def pop_flash(request: Request) -> FlashMessage | None:
    """Read a flash message from cookies without mutating the response."""
    raw = request.cookies.get(FLASH_COOKIE_NAME)
    if not raw:
        return None
    try:
        data: dict[str, Any] = json.loads(raw)
    except json.JSONDecodeError:
        return None
    message = data.get("message")
    if not message:
        return None
    level = data.get("level", "info")
    return FlashMessage(message=message, level=level)

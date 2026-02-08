import json
from typing import Any, Dict, Optional

from fastapi import Request
from fastapi.responses import Response

FLASH_COOKIE = "flash_message"


def set_flash(response: Response, message: str, category: str = "success") -> None:
    """Store a flash message in a cookie."""
    payload = json.dumps({"message": message, "category": category}, ensure_ascii=False)
    response.set_cookie(key=FLASH_COOKIE, value=payload, httponly=True)


def read_flash(request: Request) -> Optional[Dict[str, Any]]:
    """Read the flash message from the request cookie."""
    raw = request.cookies.get(FLASH_COOKIE)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None

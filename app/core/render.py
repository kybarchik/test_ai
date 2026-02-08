from typing import Any, Dict

from fastapi import Request
from fastapi.responses import HTMLResponse

from app.core.flash import FLASH_COOKIE, read_flash


def render_template(request: Request, name: str, context: Dict[str, Any]) -> HTMLResponse:
    """Render a Jinja2 template with flash messages."""
    templates = request.app.state.templates
    flash = read_flash(request)
    response = templates.TemplateResponse(name, {"request": request, "flash": flash, **context})
    if flash:
        response.delete_cookie(FLASH_COOKIE)
    return response

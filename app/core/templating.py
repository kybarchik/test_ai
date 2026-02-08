from fastapi import Request
from fastapi.responses import HTMLResponse

from app.core.flash import FLASH_COOKIE_NAME, pop_flash


def render_template(request: Request, name: str, context: dict) -> HTMLResponse:
    """Render a Jinja2 template with shared context and flash messages."""
    templates = request.app.state.templates
    flash = pop_flash(request)
    response = templates.TemplateResponse(name, {"request": request, "flash": flash, **context})
    if flash:
        response.delete_cookie(FLASH_COOKIE_NAME)
    return response

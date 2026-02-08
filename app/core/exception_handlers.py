import logging

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


def _wants_html(request: Request) -> bool:
    """Return True when the request expects HTML content."""
    accept = request.headers.get("accept", "")
    return "text/html" in accept


def register_exception_handlers(app: FastAPI) -> None:
    """Register exception handlers for HTTP and database errors."""

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):  # type: ignore[override]
        """Handle HTTP errors and redirect unauthenticated users to login."""
        if exc.status_code == 401 and _wants_html(request):
            return RedirectResponse(url="/login", status_code=302)
        if _wants_html(request):
            templates: Jinja2Templates = request.app.state.templates
            return templates.TemplateResponse(
                "error.html",
                {"request": request, "status_code": exc.status_code, "detail": exc.detail},
                status_code=exc.status_code,
            )
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):  # type: ignore[override]
        """Handle database errors with logging."""
        logger.exception("Database error", extra={"path": request.url.path})
        if _wants_html(request):
            templates: Jinja2Templates = request.app.state.templates
            return templates.TemplateResponse(
                "error.html",
                {"request": request, "status_code": 500, "detail": "Ошибка базы данных"},
                status_code=500,
            )
        return JSONResponse(status_code=500, content={"detail": "Database error"})

import logging

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db_session
from app.core.flash import set_flash
from app.core.render import render_template
from app.core.security import create_access_token
from app.services.auth_service import AuthService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request) -> HTMLResponse:
    """Render the login page."""
    return render_template(request, "login.html", {"user": None})


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_db_session),
) -> RedirectResponse | HTMLResponse:
    """Handle login form submission."""
    service = AuthService(session)
    is_valid = await service.authenticate(username=username, password=password)
    if not is_valid:
        logger.info("Login failed", extra={"username": username})
        return render_template(request, "login.html", {"error": "Неверные учетные данные", "user": None})
    logger.info("Login succeeded", extra={"username": username})
    token = create_access_token(subject=username)
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(key="access_token", value=token, httponly=True)
    set_flash(response, "Успешный вход", "success")
    return response


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, user: dict = Depends(get_current_user)) -> HTMLResponse:
    """Render the protected home page."""
    return render_template(request, "home.html", {"user": user})


@router.post("/logout")
async def logout() -> RedirectResponse:
    """Clear the auth cookie and redirect to login."""
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie(key="access_token")
    set_flash(response, "Вы вышли из системы", "info")
    return response

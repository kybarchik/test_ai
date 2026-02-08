from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db_session
from app.core.security import create_access_token
from app.services.auth_service import AuthService

router = APIRouter()


def render_template(request: Request, name: str, context: dict) -> HTMLResponse:
    """Render a Jinja2 template with the given context."""
    templates = request.app.state.templates
    return templates.TemplateResponse(name, {"request": request, **context})


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request) -> HTMLResponse:
    """Render the login page."""
    return render_template(request, "login.html", {})


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
        return render_template(request, "login.html", {"error": "Неверные учетные данные"})
    token = create_access_token(subject=username)
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return response


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, user: dict = Depends(get_current_user)) -> HTMLResponse:
    """Render the protected home page."""
    return render_template(request, "home.html", {"user": user})

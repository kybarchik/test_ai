from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.core.dependencies import get_current_user
from app.core.flash import set_flash
from app.core.templating import render_template

router = APIRouter()

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request) -> HTMLResponse:
    """Render the login page."""
    return render_template(request, "users/login.html", {"user": None})


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

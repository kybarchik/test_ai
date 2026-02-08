from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.user_service import UserService
from app.db.session import get_async_session
from app.core.templating import render_template

router = APIRouter(tags=["users"])


@router.post("/users", response_class=HTMLResponse)
async def register_user(
    request: Request,
    email: str = Form(...),
    full_name: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_async_session),
) -> HTMLResponse:
    """Register a new user."""
    service = UserService(session)
    user = await service.register_user(email=email, full_name=full_name, password=password)
    if not user:
        return render_template(
            request,
            "users/register.html",
            {"error": "Пользователь с таким email уже существует"},
        )
    return render_template(request, "users/profile.html", {"user": user})


@router.post("/login", response_class=HTMLResponse)
async def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_async_session),
) -> HTMLResponse:
    """Authenticate a user."""
    service = UserService(session)
    user = await service.authenticate_user(email=email, password=password)
    if not user:
        return render_template(request, "users/login.html", {"error": "Неверные учетные данные"})
    return render_template(request, "users/profile.html", {"user": user})


@router.get("/users/{user_id}", response_class=HTMLResponse)
async def get_user_profile(
    request: Request,
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> HTMLResponse:
    """Get a user profile."""
    service = UserService(session)
    user = await service.get_profile(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    return render_template(request, "users/profile.html", {"user": user})


@router.put("/users/{user_id}", response_class=HTMLResponse)
async def update_user(
    request: Request,
    user_id: int,
    email: str | None = Form(None),
    full_name: str | None = Form(None),
    password: str | None = Form(None),
    session: AsyncSession = Depends(get_async_session),
) -> HTMLResponse:
    """Update a user profile."""
    service = UserService(session)
    user = await service.update_user(
        user_id=user_id,
        email=email,
        full_name=full_name,
        password=password,
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    return render_template(request, "users/profile.html", {"user": user})


@router.delete("/users/{user_id}")
async def deactivate_user(
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    """Deactivate a user."""
    service = UserService(session)
    user = await service.deactivate_user(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    return {"status": "Пользователь деактивирован"}

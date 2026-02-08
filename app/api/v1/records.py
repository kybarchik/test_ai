from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db_session
from app.core.flash import set_flash
from app.core.pagination import Pagination
from app.core.render import render_template
from app.schemas.record import RecordCreate, RecordUpdate
from app.services.record_service import RecordService

router = APIRouter(prefix="/records", tags=["records"])


@router.get("/", response_class=HTMLResponse)
async def list_records(
    request: Request,
    page: int = 1,
    size: int = 10,
    user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> HTMLResponse:
    """Render the records list page."""
    pagination = Pagination(page=max(page, 1), size=min(max(size, 1), 50))
    service = RecordService(session)
    records = await service.list_records(pagination)
    return render_template(
        request,
        "records/list.html",
        {"records": records, "pagination": pagination, "user": user},
    )


@router.get("/new", response_class=HTMLResponse)
async def new_record(
    request: Request,
    user: dict = Depends(get_current_user),
) -> HTMLResponse:
    """Render the record creation form."""
    return render_template(request, "records/form.html", {"record": None, "user": user})


@router.post("/new")
async def create_record(
    request: Request,
    title: str = Form(...),
    description: str | None = Form(None),
    user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> RedirectResponse:
    """Handle record creation."""
    service = RecordService(session)
    payload = RecordCreate(title=title, description=description)
    await service.create_record(payload)
    response = RedirectResponse(url="/records", status_code=302)
    set_flash(response, "Запись создана", "success")
    return response


@router.get("/{record_id}", response_class=HTMLResponse)
async def edit_record(
    request: Request,
    record_id: int,
    user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> HTMLResponse:
    """Render the record edit form."""
    service = RecordService(session)
    record = await service.get_record(record_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Запись не найдена")
    return render_template(request, "records/form.html", {"record": record, "user": user})


@router.post("/{record_id}")
async def update_record(
    record_id: int,
    title: str = Form(...),
    description: str | None = Form(None),
    user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> RedirectResponse:
    """Handle record update."""
    service = RecordService(session)
    payload = RecordUpdate(title=title, description=description)
    record = await service.update_record(record_id, payload)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Запись не найдена")
    response = RedirectResponse(url="/records", status_code=302)
    set_flash(response, "Запись обновлена", "success")
    return response

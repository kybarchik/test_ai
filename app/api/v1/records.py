from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db_session
from app.core.flash import set_flash
from app.core.pagination import Pagination, clamp_pagination
from app.core.templating import render_template
from app.modules.records.service import RecordService
from app.schemas.record import RecordCreate, RecordUpdate

router = APIRouter(prefix="/records", tags=["records"])


@router.get("", response_class=HTMLResponse)
async def list_records(
    request: Request,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    session: AsyncSession = Depends(get_db_session),
    user: dict = Depends(get_current_user),
) -> HTMLResponse:
    """Render the list of records."""
    page, per_page = clamp_pagination(page, per_page)
    pagination = Pagination(page=page, per_page=per_page, total=0)
    service = RecordService(session)
    records, total = await service.list_records(offset=pagination.offset, limit=pagination.per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total)
    return render_template(
        request,
        "records/list.html",
        {"user": user, "records": records, "pagination": pagination},
    )


@router.get("/new", response_class=HTMLResponse)
async def new_record(
    request: Request,
    user: dict = Depends(get_current_user),
) -> HTMLResponse:
    """Render a blank record form."""
    return render_template(request, "records/form.html", {"user": user, "record": None})


@router.post("/new")
async def create_record(
    request: Request,
    title: str = Form(...),
    description: str | None = Form(None),
    session: AsyncSession = Depends(get_db_session),
    user: dict = Depends(get_current_user),
) -> RedirectResponse | HTMLResponse:
    """Create a new record and redirect to the list."""
    payload = RecordCreate(title=title, description=description)
    service = RecordService(session)
    await service.create_record(payload)
    response = RedirectResponse(url="/records", status_code=302)
    set_flash(response, "Запись создана", "success")
    return response


@router.get("/{record_id}/edit", response_class=HTMLResponse)
async def edit_record(
    request: Request,
    record_id: int,
    session: AsyncSession = Depends(get_db_session),
    user: dict = Depends(get_current_user),
) -> HTMLResponse:
    """Render edit form for a record."""
    service = RecordService(session)
    record = await service.get_record(record_id)
    if not record:
        return render_template(
            request,
            "error.html",
            {"user": user, "status_code": 404, "detail": "Запись не найдена"},
        )
    return render_template(request, "records/form.html", {"user": user, "record": record})


@router.post("/{record_id}/edit")
async def update_record(
    request: Request,
    record_id: int,
    title: str = Form(...),
    description: str | None = Form(None),
    session: AsyncSession = Depends(get_db_session),
    user: dict = Depends(get_current_user),
) -> RedirectResponse | HTMLResponse:
    """Update a record and redirect to list."""
    payload = RecordUpdate(title=title, description=description)
    service = RecordService(session)
    updated = await service.update_record(record_id, payload)
    if not updated:
        return render_template(
            request,
            "error.html",
            {"user": user, "status_code": 404, "detail": "Запись не найдена"},
        )
    response = RedirectResponse(url="/records", status_code=302)
    set_flash(response, "Запись обновлена", "success")
    return response

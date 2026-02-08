from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db_session
from app.core.templating import render_template
from app.modules.items.tasks.test_module.service import TestModuleService

router = APIRouter(prefix="/items/test-module", tags=["test-module"])


@router.get("", response_class=HTMLResponse)
async def list_test_module_items(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    user: dict = Depends(get_current_user),
) -> HTMLResponse:
    """Render list view for the example module."""
    service = TestModuleService(session)
    items = await service.list_items()
    return render_template(request, "test_module/list.html", {"user": user, "items": items})

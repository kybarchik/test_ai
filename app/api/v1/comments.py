from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.comment_service import CommentService
from app.core.dependencies import get_current_user, get_db_session
from app.core.flash import set_flash
from app.infrastructure.repositories.approval_repository import ApprovalRepository

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("")
async def add_comment(
    request: Request,
    content: str = Form(...),
    document_id: int | None = Form(None),
    approval_id: int | None = Form(None),
    session: AsyncSession = Depends(get_db_session),
    user: dict = Depends(get_current_user),
) -> RedirectResponse:
    """Create a comment and redirect back."""
    service = CommentService(session)
    comment = await service.add_comment(content, document_id, approval_id)
    redirect_url = "/documents"
    if document_id:
        redirect_url = f"/documents/{document_id}"
    elif approval_id:
        approval = await ApprovalRepository(session).get_approval(approval_id)
        if approval:
            redirect_url = f"/documents/{approval.document_id}"
    response = RedirectResponse(url=redirect_url, status_code=302)
    if not comment:
        set_flash(response, "Не удалось добавить комментарий", "error")
        return response
    set_flash(response, "Комментарий добавлен", "success")
    return response

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.approval_service import ApprovalService
from app.application.services.comment_service import CommentService
from app.core.dependencies import get_current_user, get_db_session
from app.core.flash import set_flash

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.post("/{approval_id}/steps/{step_id}/approve")
async def approve_step(
    request: Request,
    approval_id: int,
    step_id: int,
    session: AsyncSession = Depends(get_db_session),
    user: dict = Depends(get_current_user),
) -> RedirectResponse:
    """Approve approval step and redirect."""
    service = ApprovalService(session)
    step = await service.approve_step(step_id, user["id"])
    response = RedirectResponse(url="/documents", status_code=302)
    if not step or step.approval_id != approval_id:
        set_flash(response, "Не удалось согласовать шаг", "error")
        return response
    document_id = step.approval.document_id if step.approval else None
    response = RedirectResponse(
        url=f"/documents/{document_id}" if document_id else "/documents",
        status_code=302,
    )
    set_flash(response, "Шаг согласован", "success")
    return response


@router.post("/{approval_id}/steps/{step_id}/reject")
async def reject_step(
    request: Request,
    approval_id: int,
    step_id: int,
    reason: str = Form(...),
    session: AsyncSession = Depends(get_db_session),
    user: dict = Depends(get_current_user),
) -> RedirectResponse:
    """Reject approval step and redirect."""
    service = ApprovalService(session)
    step = await service.reject_step(step_id, user["id"], reason)
    response = RedirectResponse(url="/documents", status_code=302)
    if not step or step.approval_id != approval_id:
        set_flash(response, "Не удалось отклонить шаг", "error")
        return response
    document_id = step.approval.document_id if step.approval else None
    response = RedirectResponse(
        url=f"/documents/{document_id}" if document_id else "/documents",
        status_code=302,
    )
    set_flash(response, "Шаг отклонен", "success")
    return response


@router.post("/{approval_id}/steps/{step_id}/revision")
async def request_revision(
    request: Request,
    approval_id: int,
    step_id: int,
    reason: str = Form(...),
    session: AsyncSession = Depends(get_db_session),
    user: dict = Depends(get_current_user),
) -> RedirectResponse:
    """Request revision for an approval step and redirect."""
    service = ApprovalService(session)
    step = await service.request_revision_step(step_id, user["id"], reason)
    response = RedirectResponse(url="/documents", status_code=302)
    if not step or step.approval_id != approval_id:
        set_flash(response, "Не удалось отправить на доработку", "error")
        return response
    document_id = step.approval.document_id if step.approval else None
    response = RedirectResponse(
        url=f"/documents/{document_id}" if document_id else "/documents",
        status_code=302,
    )
    set_flash(response, "Шаг отправлен на доработку", "success")
    return response


@router.get("/{approval_id}/comments")
async def list_approval_comments(
    approval_id: int,
    session: AsyncSession = Depends(get_db_session),
    user: dict = Depends(get_current_user),
) -> JSONResponse:
    """Return comments for an approval."""
    service = CommentService(session)
    comments = await service.list_for_approval(approval_id)
    payload = [
        {
            "id": comment.id,
            "content": comment.content,
            "document_id": comment.document_id,
            "approval_id": comment.approval_id,
            "created_at": comment.created_at.isoformat(),
        }
        for comment in comments
    ]
    return JSONResponse(payload)

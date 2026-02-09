from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.approval_service import ApprovalService
from app.application.services.comment_service import CommentService
from app.application.services.document_metric_service import DocumentMetricService
from app.application.services.document_service import DocumentService
from app.core.dependencies import get_current_user, get_db_session
from app.core.flash import set_flash
from app.core.templating import render_template
from app.domain.enums import ApprovalStatus, ApprovalStepStatus, DocumentStatus
from app.schemas.document import DocumentCreate, DocumentUpdate

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_class=HTMLResponse)
async def list_documents(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    user: dict = Depends(get_current_user),
) -> HTMLResponse:
    """Render the list of documents."""
    service = DocumentService(session)
    documents = await service.list_documents()
    return render_template(
        request,
        "documents/list.html",
        {"user": user, "documents": documents},
    )


@router.post("")
async def create_document(
    request: Request,
    title: str = Form(...),
    description: str | None = Form(None),
    session: AsyncSession = Depends(get_db_session),
    user: dict = Depends(get_current_user),
) -> RedirectResponse:
    """Create a draft document and redirect to detail."""
    payload = DocumentCreate(title=title, description=description)
    service = DocumentService(session)
    document = await service.create_draft(payload)
    response = RedirectResponse(url=f"/documents/{document.id}", status_code=302)
    set_flash(response, "Черновик создан", "success")
    return response


@router.get("/{document_id}", response_class=HTMLResponse)
async def get_document(
    request: Request,
    document_id: int,
    session: AsyncSession = Depends(get_db_session),
    user: dict = Depends(get_current_user),
) -> HTMLResponse:
    """Render a document detail page."""
    service = DocumentService(session)
    approval_service = ApprovalService(session)
    comment_service = CommentService(session)
    metric_service = DocumentMetricService(session)
    document = await service.get_document(document_id)
    if not document:
        return render_template(
            request,
            "error.html",
            {"user": user, "status_code": 404, "detail": "Документ не найден"},
        )
    approval, steps = await approval_service.get_approval_with_steps(document.id)
    document_comments = await comment_service.list_for_document(document.id)
    approval_comments = await comment_service.list_for_approval(approval.id) if approval else []
    metrics = await metric_service.list_metrics_for_document(document.id)
    status_labels = {
        DocumentStatus.DRAFT.value: "Черновик",
        DocumentStatus.APPROVAL.value: "Согласование",
        DocumentStatus.REVISION_REQUIRED.value: "Требует доработки",
        DocumentStatus.CANCELED.value: "Отменено",
        DocumentStatus.APPROVED.value: "Согласовано",
    }
    approval_status_labels = {
        ApprovalStatus.PENDING.value: "Ожидает",
        ApprovalStatus.APPROVED.value: "Согласовано",
        ApprovalStatus.REJECTED.value: "Отклонено",
    }
    step_status_labels = {
        ApprovalStepStatus.PENDING.value: "Ожидает",
        ApprovalStepStatus.APPROVED.value: "Согласовано",
        ApprovalStepStatus.REJECTED.value: "Отклонено",
    }
    return render_template(
        request,
        "documents/detail.html",
        {
            "user": user,
            "document": document,
            "approval": approval,
            "approval_steps": steps,
            "document_comments": document_comments,
            "approval_comments": approval_comments,
            "metrics": metrics,
            "status_labels": status_labels,
            "approval_status_labels": approval_status_labels,
            "step_status_labels": step_status_labels,
        },
    )


@router.post("/{document_id}/submit")
async def submit_document(
    request: Request,
    document_id: int,
    approver_ids: str = Form(...),
    session: AsyncSession = Depends(get_db_session),
    user: dict = Depends(get_current_user),
) -> RedirectResponse:
    """Submit a document for approval."""
    approvers = [int(item.strip()) for item in approver_ids.split(",") if item.strip()]
    service = ApprovalService(session)
    approval = await service.create_approval_flow(document_id, approvers)
    response = RedirectResponse(url=f"/documents/{document_id}", status_code=302)
    if not approval:
        set_flash(response, "Не удалось отправить на согласование", "error")
        return response
    set_flash(response, "Документ отправлен на согласование", "success")
    return response


@router.put("/{document_id}")
async def update_document(
    request: Request,
    document_id: int,
    title: str = Form(...),
    description: str | None = Form(None),
    session: AsyncSession = Depends(get_db_session),
    user: dict = Depends(get_current_user),
) -> JSONResponse:
    """Update a draft document."""
    payload = DocumentUpdate(title=title, description=description)
    service = DocumentService(session)
    document = await service.update_draft(document_id, payload)
    if not document:
        return JSONResponse({"detail": "Документ не найден"}, status_code=404)
    return JSONResponse({"redirect_url": f"/documents/{document.id}"})


@router.delete("/{document_id}")
async def archive_document(
    request: Request,
    document_id: int,
    session: AsyncSession = Depends(get_db_session),
    user: dict = Depends(get_current_user),
) -> JSONResponse:
    """Archive a draft document."""
    service = DocumentService(session)
    document = await service.archive_document(document_id)
    if not document:
        return JSONResponse({"detail": "Документ не найден"}, status_code=404)
    return JSONResponse({"redirect_url": "/documents"})


@router.get("/{document_id}/comments")
async def list_document_comments(
    document_id: int,
    session: AsyncSession = Depends(get_db_session),
    user: dict = Depends(get_current_user),
) -> JSONResponse:
    """Return comments for a document."""
    service = CommentService(session)
    comments = await service.list_for_document(document_id)
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


@router.post("/{document_id}/metrics")
async def add_document_metric(
    request: Request,
    document_id: int,
    name: str = Form(...),
    value: str = Form(...),
    unit: str = Form(...),
    session: AsyncSession = Depends(get_db_session),
    user: dict = Depends(get_current_user),
) -> RedirectResponse:
    """Add a metric to a document."""
    service = DocumentMetricService(session)
    metric = await service.add_metric(document_id=document_id, name=name, value=value, unit=unit)
    response = RedirectResponse(url=f"/documents/{document_id}", status_code=302)
    if not metric:
        set_flash(response, "Не удалось добавить метрику", "error")
        return response
    set_flash(response, "Метрика добавлена", "success")
    return response


@router.put("/{document_id}/metrics/{metric_id}")
async def update_document_metric(
    request: Request,
    document_id: int,
    metric_id: int,
    name: str = Form(...),
    value: str = Form(...),
    unit: str = Form(...),
    session: AsyncSession = Depends(get_db_session),
    user: dict = Depends(get_current_user),
) -> JSONResponse:
    """Update a metric in a document."""
    service = DocumentMetricService(session)
    metric = await service.update_metric(
        document_id=document_id,
        metric_id=metric_id,
        name=name,
        value=value,
        unit=unit,
    )
    if not metric:
        return JSONResponse({"detail": "Не удалось обновить метрику"}, status_code=400)
    return JSONResponse({"redirect_url": f"/documents/{document_id}"})


@router.delete("/{document_id}/metrics/{metric_id}")
async def delete_document_metric(
    request: Request,
    document_id: int,
    metric_id: int,
    session: AsyncSession = Depends(get_db_session),
    user: dict = Depends(get_current_user),
) -> JSONResponse:
    """Delete a metric from a document."""
    service = DocumentMetricService(session)
    removed = await service.delete_metric(document_id=document_id, metric_id=metric_id)
    if not removed:
        return JSONResponse({"detail": "Не удалось удалить метрику"}, status_code=400)
    return JSONResponse({"redirect_url": f"/documents/{document_id}"})

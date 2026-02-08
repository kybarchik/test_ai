from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.document_service import DocumentService
from app.core.dependencies import get_current_user, get_db_session
from app.core.flash import set_flash
from app.core.templating import render_template
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
    document = await service.get_document(document_id)
    if not document:
        return render_template(
            request,
            "error.html",
            {"user": user, "status_code": 404, "detail": "Документ не найден"},
        )
    return render_template(
        request,
        "documents/detail.html",
        {"user": user, "document": document},
    )


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

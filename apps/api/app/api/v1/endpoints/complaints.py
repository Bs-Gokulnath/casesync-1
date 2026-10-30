from datetime import date

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.v1.deps import require_csrf, require_permission
from app.db.session import get_db
from app.models.enums import ComplaintPriority, ComplaintStatus
from app.models.user import User
from app.schemas.common import Page
from app.schemas.complaint import (
    ComplaintCreate,
    ComplaintOut,
    ComplaintUpdate,
    RelationshipCreate,
    RelationshipOut,
)
from app.schemas.document import DocumentOut
from app.schemas.history import TimelineEntry
from app.schemas.workflow import (
    AssignRequest,
    DisposeRequest,
    EscalateRequest,
    ReopenRequest,
    TransferRequest,
    TransitionRequest,
)
from app.security.permissions import Permission
from app.services import complaint_service, document_service, workflow_service
from app.services.complaint_service import (
    RelatedComplaintNotFoundError,
    ScopeError,
    SelfRelationshipError,
)
from app.services.document_service import DocumentNotFoundError, InvalidUploadError
from app.services.workflow_service import ComplaintNotFoundError, IllegalTransitionError

router = APIRouter(prefix="/complaints", tags=["complaints"])


def _illegal_transition_response(exc: IllegalTransitionError) -> HTTPException:
    return HTTPException(status.HTTP_409_CONFLICT, detail=str(exc))


@router.get("", response_model=Page[ComplaintOut])
def list_complaints(
    status_: ComplaintStatus | None = Query(default=None, alias="status"),
    bureau_id: int | None = None,
    priority: ComplaintPriority | None = None,
    category_id: int | None = None,
    institution_id: int | None = None,
    assigned_officer_id: int | None = None,
    q: str | None = None,
    received_from: date | None = None,
    received_to: date | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(require_permission(Permission.COMPLAINT_READ)),
) -> Page[ComplaintOut]:
    return complaint_service.list_complaints(
        db,
        current_user=user,
        status=status_,
        bureau_id=bureau_id,
        priority=priority,
        category_id=category_id,
        institution_id=institution_id,
        assigned_officer_id=assigned_officer_id,
        q=q,
        received_from=received_from,
        received_to=received_to,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=ComplaintOut, status_code=status.HTTP_201_CREATED)
def create_complaint(
    payload: ComplaintCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission(Permission.COMPLAINT_CREATE)),
    _csrf: None = Depends(require_csrf),
) -> ComplaintOut:
    try:
        return complaint_service.create_complaint(db, payload, current_user=user)
    except ScopeError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{complaint_id}", response_model=ComplaintOut)
def get_complaint(
    complaint_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission(Permission.COMPLAINT_READ)),
) -> ComplaintOut:
    complaint = complaint_service.get_complaint(db, complaint_id)
    if complaint is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Complaint not found")
    return complaint


@router.get("/{complaint_id}/history", response_model=list[TimelineEntry])
def get_complaint_history(
    complaint_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission(Permission.COMPLAINT_READ)),
) -> list[TimelineEntry]:
    if complaint_service.get_complaint(db, complaint_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Complaint not found")
    return complaint_service.get_timeline(db, complaint_id)


@router.patch("/{complaint_id}", response_model=ComplaintOut)
def update_complaint(
    complaint_id: int,
    payload: ComplaintUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission(Permission.COMPLAINT_EDIT)),
    _csrf: None = Depends(require_csrf),
) -> ComplaintOut:
    updated = complaint_service.update_complaint(db, complaint_id, payload, current_user=user)
    if updated is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Complaint not found")
    return updated


@router.get("/{complaint_id}/relationships", response_model=list[RelationshipOut])
def list_relationships(
    complaint_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission(Permission.COMPLAINT_READ)),
) -> list[RelationshipOut]:
    return [
        RelationshipOut.model_validate(r)
        for r in complaint_service.get_relationships(db, complaint_id)
    ]


@router.post(
    "/{complaint_id}/relationships",
    response_model=RelationshipOut,
    status_code=status.HTTP_201_CREATED,
)
def create_relationship(
    complaint_id: int,
    payload: RelationshipCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission(Permission.COMPLAINT_RELATE)),
    _csrf: None = Depends(require_csrf),
) -> RelationshipOut:
    try:
        relationship = complaint_service.create_relationship(
            db, complaint_id, payload, current_user=user
        )
        return RelationshipOut.model_validate(relationship)
    except SelfRelationshipError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RelatedComplaintNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{complaint_id}/transition", response_model=ComplaintOut)
def transition_complaint(
    complaint_id: int,
    payload: TransitionRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission(Permission.COMPLAINT_TRANSITION)),
    _csrf: None = Depends(require_csrf),
) -> ComplaintOut:
    try:
        return workflow_service.transition(
            db, complaint_id, payload.to_status, actor=user, reason=payload.reason
        )
    except ComplaintNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except IllegalTransitionError as exc:
        raise _illegal_transition_response(exc) from exc


@router.post("/{complaint_id}/transfer", response_model=ComplaintOut)
def transfer_complaint(
    complaint_id: int,
    payload: TransferRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission(Permission.COMPLAINT_TRANSFER)),
    _csrf: None = Depends(require_csrf),
) -> ComplaintOut:
    try:
        return workflow_service.transfer(
            db, complaint_id, to_bureau_id=payload.to_bureau_id, reason=payload.reason, actor=user
        )
    except ComplaintNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except IllegalTransitionError as exc:
        raise _illegal_transition_response(exc) from exc


@router.post("/{complaint_id}/escalate", response_model=ComplaintOut)
def escalate_complaint(
    complaint_id: int,
    payload: EscalateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission(Permission.COMPLAINT_ESCALATE)),
    _csrf: None = Depends(require_csrf),
) -> ComplaintOut:
    try:
        return workflow_service.escalate(db, complaint_id, reason=payload.reason, actor=user)
    except ComplaintNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except IllegalTransitionError as exc:
        raise _illegal_transition_response(exc) from exc


@router.post("/{complaint_id}/dispose", response_model=ComplaintOut)
def dispose_complaint(
    complaint_id: int,
    payload: DisposeRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission(Permission.COMPLAINT_DISPOSE)),
    _csrf: None = Depends(require_csrf),
) -> ComplaintOut:
    try:
        return workflow_service.dispose(
            db, complaint_id, disposal_note=payload.disposal_note, actor=user
        )
    except ComplaintNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except IllegalTransitionError as exc:
        raise _illegal_transition_response(exc) from exc


@router.post("/{complaint_id}/reopen", response_model=ComplaintOut)
def reopen_complaint(
    complaint_id: int,
    payload: ReopenRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission(Permission.COMPLAINT_REOPEN)),
    _csrf: None = Depends(require_csrf),
) -> ComplaintOut:
    try:
        return workflow_service.reopen(db, complaint_id, reason=payload.reason, actor=user)
    except ComplaintNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except IllegalTransitionError as exc:
        raise _illegal_transition_response(exc) from exc


@router.post("/{complaint_id}/assign", response_model=ComplaintOut)
def assign_complaint(
    complaint_id: int,
    payload: AssignRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission(Permission.COMPLAINT_ASSIGN)),
    _csrf: None = Depends(require_csrf),
) -> ComplaintOut:
    try:
        return workflow_service.assign(db, complaint_id, officer_id=payload.officer_id, actor=user)
    except ComplaintNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/{complaint_id}/documents", response_model=list[DocumentOut])
def list_documents(
    complaint_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission(Permission.DOCUMENT_READ)),
) -> list[DocumentOut]:
    return [
        DocumentOut.model_validate(doc)
        for doc in document_service.list_for_complaint(db, complaint_id)
    ]


@router.post(
    "/{complaint_id}/documents",
    response_model=DocumentOut,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    complaint_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_permission(Permission.DOCUMENT_UPLOAD)),
    _csrf: None = Depends(require_csrf),
) -> DocumentOut:
    content = await file.read()
    try:
        document = document_service.upload_document(db, complaint_id, file, content, actor=user)
        return DocumentOut.model_validate(document)
    except InvalidUploadError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{complaint_id}/documents/{document_id}")
def download_document(
    complaint_id: int,
    document_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission(Permission.DOCUMENT_READ)),
) -> FileResponse:
    try:
        document, path = document_service.get_file_path(db, complaint_id, document_id)
    except DocumentNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return FileResponse(path, media_type=document.content_type, filename=document.file_name)

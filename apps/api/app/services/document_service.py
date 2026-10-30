import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.document import Document
from app.models.user import User
from app.services import audit_service

settings = get_settings()

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


class InvalidUploadError(Exception):
    pass


class DocumentNotFoundError(Exception):
    pass


def _complaint_storage_dir(complaint_id: int) -> Path:
    directory = settings.upload_storage_path / str(complaint_id)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def upload_document(
    db: Session, complaint_id: int, file: UploadFile, content: bytes, *, actor: User
) -> Document:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise InvalidUploadError(f"Unsupported file type: {file.content_type}")

    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise InvalidUploadError(f"File exceeds the {settings.max_upload_mb}MB upload limit")

    original_name = Path(file.filename or "upload").name  # strip any path components
    stored_name = f"{uuid.uuid4().hex}_{original_name}"
    directory = _complaint_storage_dir(complaint_id)
    (directory / stored_name).write_bytes(content)

    document = Document(
        complaint_id=complaint_id,
        file_name=original_name,
        stored_path=f"{complaint_id}/{stored_name}",
        content_type=file.content_type or "application/octet-stream",
        size_bytes=len(content),
        uploaded_by=actor.id,
    )
    db.add(document)
    db.flush()
    audit_service.record(
        db,
        actor_id=actor.id,
        action="document.upload",
        entity_type="document",
        entity_id=str(document.id),
        after={"complaint_id": complaint_id, "file_name": original_name},
    )
    db.commit()
    return document


def list_for_complaint(db: Session, complaint_id: int) -> list[Document]:
    return list(
        db.scalars(
            select(Document).where(
                Document.complaint_id == complaint_id, Document.is_deleted.is_(False)
            )
        )
    )


def get_file_path(db: Session, complaint_id: int, document_id: int) -> tuple[Document, Path]:
    document = db.get(Document, document_id)
    if document is None or document.is_deleted or document.complaint_id != complaint_id:
        raise DocumentNotFoundError(f"Document {document_id} not found")
    path = settings.upload_storage_path / document.stored_path
    if not path.is_file():
        raise DocumentNotFoundError("Stored file is missing")
    return document, path

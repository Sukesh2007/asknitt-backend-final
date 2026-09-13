import os
import re

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Attachment, Question
from app.oauth import get_current_user
from app.schema import AttachmentResponse, AttachmentAccessResponse
from app.services.storage import upload_file, delete_file, create_signed_url


router = APIRouter(
    prefix="/attachments",
    tags=["Attachments"]
)


MAX_FILE_SIZE = 10 * 1024 * 1024

ALLOWED_FILE_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/webp"
}


def sanitize_filename(filename: str) -> str:
    filename = os.path.basename(filename)

    filename = re.sub(
        r"[^a-zA-Z0-9._-]",
        "_",
        filename
    )

    if not filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file name"
        )

    return filename


@router.post(
    "/questions/{question_id}",
    response_model=AttachmentResponse,
    status_code=status.HTTP_201_CREATED
)
async def upload_attachment(
    question_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    print(file.filename)
    print(file.content_type)

    if file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type {file.content_type}"
        )

    question = (
        db.query(Question)
        .filter(Question.id == question_id)
        .first()
    )

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )

    if question.owner_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only attach files to your own question"
        )

    file_bytes = await file.read()

    file_size = len(file_bytes)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size must not exceed 10 MB"
        )

    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File cannot be empty"
        )

    file_name = sanitize_filename(
        file.filename or "file"
    )

    attachment = Attachment(
        question_id=question_id,
        file_name=file_name,
        file_type=file.content_type,
        file_size=file_size,
        storage_path=""
    )

    db.add(attachment)
    db.flush()

    storage_path = (
        f"questions/"
        f"{question_id}/"
        f"{attachment.id}/"
        f"{file_name}"
    )

    attachment.storage_path = storage_path

    uploaded = False

    try:
        upload_file(
            file_bytes=file_bytes,
            storage_path=storage_path,
            content_type=file.content_type
        )

        uploaded = True

        db.commit()
        db.refresh(attachment)

        return attachment

    except Exception:
        db.rollback()

        if uploaded:
            try:
                delete_file(storage_path)
            except Exception:
                pass

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload attachment"
        )

@router.get(
    "/{attachment_id}",
    response_model=AttachmentAccessResponse
)
async def get_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    attachment = (
        db.query(Attachment)
        .filter(Attachment.id == attachment_id)
        .first()
    )

    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found"
        )

    try:
        url = create_signed_url(
            storage_path=attachment.storage_path
        )

        return AttachmentAccessResponse(
            id=attachment.id,
            question_id=attachment.question_id,
            file_name=attachment.file_name,
            file_type=attachment.file_type,
            file_size=attachment.file_size,
            storage_path=attachment.storage_path,
            url=url
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate file URL"
        )
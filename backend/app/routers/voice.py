from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.voice_service import enroll_student_voice_embedding, verify_student_voice_embedding

router = APIRouter(
    prefix="/students",
    tags=["Biometrics"]
)

@router.post("/{student_id}/voice/enroll")
async def enroll_voice(
        student_id: int,
        audio: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    try:
        audio_bytes = await audio.read()

        if not audio_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty"
            )

        enroll_student_voice_embedding(
            db=db,
            student_id=student_id,
            audio_bytes=audio_bytes
        )

        return {"message": "Voice embedding enrolled successfully."}
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )

@router.post("/{student_id}/voice/verify")
async def verify_student_voice(
        student_id: int,
        audio: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    try:
        audio_bytes = await audio.read()

        if not audio_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty"
            )

        is_verified = verify_student_voice_embedding(
            db=db,
            student_id=student_id,
            audio_bytes=audio_bytes
        )

        return {"verified": is_verified}
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )

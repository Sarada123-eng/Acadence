from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.face_service import identify_students_in_classroom
from app.services.voice_service import identify_students_in_classroom_by_voice
import cv2
import numpy as np

router = APIRouter(
    prefix="/classrooms",
    tags=["Classrooms"]
)

@router.post("/{classroom_id}/face/identify")
async def identify_students_by_face(
    classroom_id: int,
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        image_bytes = await image.read()

        if not image_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty"
            )

        image_array = np.frombuffer(
            image_bytes,
            dtype=np.uint8
        )  # convert bytes to numpy array

        image = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR
        )  # decode numpy array to image

        if image is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is not a valid image"
            )
        # convert BGR to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        student_ids = identify_students_in_classroom(
            db=db,
            classroom_id=classroom_id,
            image=image
        )

        if not student_ids:
            return {"message": "No students identified in the classroom image."}

        return {"classroom_id": classroom_id, "identified_student_ids": student_ids}
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )

@router.post("/{classroom_id}/voice/identify")
async def identify_students_by_voice(
        classroom_id: int,
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

        identified_students = identify_students_in_classroom_by_voice(
            db=db,
            classroom_id=classroom_id,
            audio_bytes=audio_bytes
        )

        if not identified_students:
            return {"message": "No students identified in the classroom audio."}

        return {"classroom_id": classroom_id, "identified_student_ids": identified_students}
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )

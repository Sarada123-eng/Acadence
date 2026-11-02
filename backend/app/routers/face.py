from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
import cv2
from app.services.face_service import enroll_student_face_embedding, verify_student_face_embedding
import numpy as np

router = APIRouter(
    prefix="/students",
    tags=["Biometrics"]
)

@router.post("/{student_id}/face/enroll")
async def enroll_student_face(
    student_id: int,
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
        ) # convert bytes to numpy array

        image = cv2.imdecode(
            image_array, 
            cv2.IMREAD_COLOR
            ) # decode numpy array to image

        if image is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is not a valid image"
            )

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        enroll_student_face_embedding(
            db=db,
            student_id=student_id,
            image=image
        )

        return {"message": "Face embedding enrolled successfully."}
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )

@router.post("/{student_id}/face/verify")
async def verify_student_face(
    student_id: int,
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
        ) # convert bytes to numpy array

        image = cv2.imdecode(
            image_array, 
            cv2.IMREAD_COLOR
            ) # decode numpy array to image

        if image is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is not a valid image"
            )

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        is_verified = verify_student_face_embedding(
            db=db,
            student_id=student_id,
            image=image
        )

        return {"verified": is_verified}
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )

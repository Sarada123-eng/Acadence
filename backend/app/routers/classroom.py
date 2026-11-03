from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.face_service import identify_students_in_classroom
from app.services.voice_service import identify_students_in_classroom_by_voice
from app.schemas.classroom import (
    ClassroomCreate,
    ClassroomJoinRequest,
    ClassroomJoinResponse,
    ClassroomResponse,
    SubjectCreate,
    SubjectResponse,
)
from app.services.classroom_service import (
    create_classroom,
    create_subject,
    get_teacher_classrooms,
    join_classroom,
)
import cv2
import numpy as np

router = APIRouter(
    prefix="/classrooms",
    tags=["Classrooms"]
)


@router.post(
    "/teachers/{teacher_id}/subjects",
    response_model=SubjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_teacher_subject(
    teacher_id: int,
    subject: SubjectCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_subject(
            db,
            teacher_id,
            subject.name,
            subject.subject_code,
            subject.section,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "/subjects/{subject_id}/classrooms",
    response_model=ClassroomResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_subject_classroom(
    subject_id: int,
    classroom: ClassroomCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_classroom(
            db,
            subject_id,
            classroom.name,
            classroom.section,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/teachers/{teacher_id}",
    response_model=list[ClassroomResponse],
)
def list_teacher_classrooms(
    teacher_id: int,
    db: Session = Depends(get_db),
):
    return get_teacher_classrooms(db, teacher_id)


@router.post(
    "/join",
    response_model=ClassroomJoinResponse,
)
def join_classroom_by_code(
    request: ClassroomJoinRequest,
    db: Session = Depends(get_db),
):
    try:
        classroom, newly_joined = join_classroom(
            db,
            request.join_code.strip(),
            request.student_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return ClassroomJoinResponse(
        classroom_id=classroom.id,
        student_id=request.student_id,
        joined=True,
        message=(
            "Student joined the classroom."
            if newly_joined
            else "Student was already enrolled in the classroom."
        ),
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

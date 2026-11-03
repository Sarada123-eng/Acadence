from datetime import datetime

from pydantic import BaseModel, Field


class SubjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    subject_code: str = Field(min_length=1, max_length=20)
    section: str | None = Field(default=None, max_length=20)


class SubjectResponse(BaseModel):
    id: int
    name: str
    subject_code: str
    section: str | None
    teacher_id: int | None

    model_config = {"from_attributes": True}


class ClassroomCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    section: str | None = Field(default=None, max_length=20)


class ClassroomResponse(BaseModel):
    id: int
    name: str
    section: str | None
    subject_id: int
    join_code: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ClassroomJoinRequest(BaseModel):
    join_code: str = Field(min_length=1, max_length=64)
    student_id: int


class ClassroomJoinResponse(BaseModel):
    classroom_id: int
    student_id: int
    joined: bool
    message: str

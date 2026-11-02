from pydantic import BaseModel, Field


class StudentCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)


class StudentResponse(BaseModel):
    id: int
    name: str
    face_embedding_enrolled: bool
    voice_embedding_enrolled: bool

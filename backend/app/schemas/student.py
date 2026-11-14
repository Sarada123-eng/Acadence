from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class StudentCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)


class StudentRegistrationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    institutional_student_id: str = Field(min_length=1, max_length=100)
    institutional_email: str = Field(min_length=3, max_length=320)

    @field_validator("institutional_email")
    @classmethod
    def validate_email_format(cls, value: str) -> str:
        value = value.strip()
        local_part, separator, domain = value.rpartition("@")
        if (
            not separator
            or not local_part
            or not domain
            or any(character.isspace() for character in value)
            or "." not in domain
        ):
            raise ValueError("Enter a valid institutional email address.")
        return value


class StudentRegistrationResponse(BaseModel):
    registration_reference: UUID
    account_status: str
    pending_registration_expires_at: datetime


class StudentResponse(BaseModel):
    id: int
    name: str
    face_embedding_enrolled: bool
    voice_embedding_enrolled: bool

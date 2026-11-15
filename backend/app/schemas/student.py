from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class StudentRegistrationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    institutional_student_id: str = Field(min_length=1, max_length=100)
    institutional_email: str = Field(min_length=3, max_length=320)

    @field_validator("name", "institutional_student_id", mode="before")
    @classmethod
    def trim_identity_values(cls, value: str) -> str:
        if not isinstance(value, str):
            return value
        return value.strip()

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not 2 <= len(value) <= 100:
            raise ValueError("Name must contain between 2 and 100 characters.")
        return value

    @field_validator("institutional_student_id")
    @classmethod
    def validate_student_id(cls, value: str) -> str:
        if not value:
            raise ValueError("Institutional student ID cannot be empty.")
        return value

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


class StudentEmailOtpVerificationRequest(BaseModel):
    registration_reference: UUID
    otp: str = Field(
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
    )


class StudentEmailOtpVerificationResponse(BaseModel):
    registration_reference: UUID
    account_status: str

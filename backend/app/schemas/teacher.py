from pydantic import BaseModel, Field

class TeacherRegister(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50
    )

    name: str = Field(
        min_length=2,
        max_length=100
    )

    password: str = Field(
        min_length=8,
        max_length=128
    )

class TeacherLogin(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50
    )

    password: str = Field(
        min_length=8,
        max_length=128
    )

class TeacherResponse(BaseModel):
    id: int
    username: str
    name: str

    model_config = {"from_attributes": True}


class TeacherTokenResponse(TeacherResponse):
    access_token: str
    token_type: str

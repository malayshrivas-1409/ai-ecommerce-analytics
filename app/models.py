from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    count: int = Field(
        gt=0,
        le=1000,
        description="Number of events to generate"
    )


class GenerateResponse(BaseModel):
    status: str
    events_generated: int
    message: str


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
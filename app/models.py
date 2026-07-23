from pydantic import BaseModel, EmailStr, Field


# ============================================================================
# GENERATION MODELS
# ============================================================================

class GenerateRequest(BaseModel):
    """Request model for event generation"""
    count: int = Field(
        gt=0,
        le=1000,
        description="Number of events to generate",
    )


class GenerateResponse(BaseModel):
    """Response model for event generation"""
    status: str
    events_generated: int
    message: str


# ============================================================================
# AUTHENTICATION MODELS
# ============================================================================

class SignupRequest(BaseModel):
    """Request model for user registration"""
    username: str
    email: EmailStr
    password: str


class SignupResponse(BaseModel):
    """Response model for user registration"""
    status: str
    message: str


class LoginRequest(BaseModel):
    """Request model for user login"""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Response model for authentication token"""
    access_token: str
    token_type: str

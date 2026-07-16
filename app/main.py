import os

from fastapi import FastAPI, HTTPException, status
from fastapi import Depends
from app.security import get_current_user

from app.generator import generate_events
from app.uploader import upload_file
from app.models import GenerateRequest, GenerateResponse
from app.security import (
    authenticate_user,
    create_access_token
)

from app.models import (
    LoginRequest,
    TokenResponse
)
app = FastAPI(
    title="AI E-Commerce Analytics API",
    version="1.0.0",
    description="Backend API for AI Powered E-Commerce Analytics Project"
)


@app.get("/")
def home():
    return {
        "message": "Welcome to AI E-Commerce Analytics API"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
@app.post(
    "/login",
    response_model=TokenResponse
)
def login(request: LoginRequest):

    user = authenticate_user(
        request.username,
        request.password
    )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    access_token = create_access_token(
        data={
            "sub": user["username"]
        }
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer"
    )

@app.post("/generate")
def generate(
    request: GenerateRequest,
    current_user: str = Depends(get_current_user)
):

    # Step 1: Generate events
    log_file = generate_events(request.count)

    # Step 2: Upload to S3
    success = upload_file(log_file)

    if success:

        # Step 3: Delete local file
        os.remove(log_file)

        return GenerateResponse(
            status="success",
            events_generated=request.count,
            message="Events generated and uploaded successfully."
        )

    raise HTTPException(
        status_code=500,
        detail="Unable to upload file to Amazon S3."
    )
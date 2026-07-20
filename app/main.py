import os

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.generator import generate_events
from app.uploader import upload_file

from app.database import get_db, engine, Base
from app.db_models import User
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request

from app.models import (
    GenerateRequest,
    GenerateResponse,
    LoginRequest,
    TokenResponse,
    SignupRequest,
    SignupResponse
)

from app.security import (
    authenticate_user,
    create_access_token,
    get_current_user,
    hash_password
)


app = FastAPI(
    title="AI E-Commerce Analytics API",
    version="1.0.0",
    description="Backend API for AI Powered E-Commerce Analytics Project"
)

# ✓ FIXED: Use relative paths without 'app/' prefix
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

# ✓ FIXED: Use relative paths without 'app/' prefix
templates = Jinja2Templates(
    directory="templates"
)

# Create database tables if they don't exist
Base.metadata.create_all(bind=engine)

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# -------------------------
# SIGNUP
# -------------------------

@app.post(
    "/signup",
    response_model=SignupResponse
)
def signup(
    request: SignupRequest,
    db: Session = Depends(get_db)
):

    # Check if username or email already exists
    existing_user = db.query(User).filter(
        or_(
            User.username == request.username,
            User.email == request.email
        )
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username or email already registered"
        )

    # Hash password before storing it
    password_hash = hash_password(
        request.password
    )

    # Create new database user
    new_user = User(
        username=request.username,
        email=request.email,
        password_hash=password_hash
    )

    db.add(new_user)

    try:
        db.commit()
        db.refresh(new_user)

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to create user"
        )

    return SignupResponse(
        status="success",
        message="User registered successfully"
    )


# -------------------------
# LOGIN
# -------------------------

@app.post(
    "/login",
    response_model=TokenResponse
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):

    user = authenticate_user(
        db,
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
            "sub": user.username
        }
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer"
    )


# -------------------------
# GENERATE EVENTS
# -------------------------

@app.post("/generate")
def generate(
    request: GenerateRequest,
    current_user: str = Depends(get_current_user)
):

    # Generate orders, clicks and cart event files
    log_files = generate_events(
        request.count
    )

    uploaded_files = []

    # Upload each generated file
    for log_file in log_files:

        success = upload_file(log_file)

        if success:

            uploaded_files.append(
                os.path.basename(log_file)
            )

            # Delete local file after successful upload
            os.remove(log_file)

        else:

            raise HTTPException(
                status_code=500,
                detail=(
                    f"Unable to upload "
                    f"{os.path.basename(log_file)} "
                    f"to Amazon S3."
                )
            )

    return GenerateResponse(
        status="success",
        events_generated=request.count,
        message="Events generated and uploaded successfully."
    )
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.db_models import User
from app.generator import generate_events
from app.models import (
    GenerateRequest,
    GenerateResponse,
    LoginRequest,
    SignupRequest,
    SignupResponse,
    TokenResponse,
)
from app.security import (
    authenticate_user,
    create_access_token,
    get_current_user,
    hash_password,
)
from app.uploader import upload_file
from app import analytics
from app.event_scheduler import event_scheduler


# ============================================================================
# CONFIGURATION - ALLOWED DOMAINS/EMAILS FOR SECURITY
# ============================================================================

ALLOWED_EMAIL_DOMAINS = os.getenv(
    "ALLOWED_EMAIL_DOMAINS",
    "malay-comm.com,company.com"  # Whitelist domains, comma-separated
).split(",")

ALLOWED_EMAILS = os.getenv(
    "ALLOWED_EMAILS",
    ""  # Optional: specific emails, comma-separated
).split(",") if os.getenv("ALLOWED_EMAILS") else []


# ============================================================================
# APPLICATION SETUP
# ============================================================================

app = FastAPI(
    title="AI E-Commerce Analytics API",
    version="1.0.0",
    description="Backend API for AI Powered E-Commerce Analytics Project",
)

BASE_DIR = Path(__file__).resolve().parent

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static",
)

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

Base.metadata.create_all(bind=engine)


# ============================================================================
# HEALTH & HOME ENDPOINTS
# ============================================================================

@app.get("/")
def home(request: Request):
    """Serve the home page"""
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"request": request},
    )


@app.get("/login")
def login_page(request: Request):
    """Serve the login page"""
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"request": request},
    )


@app.get("/signup")
def signup_page(request: Request):
    """Serve the signup page"""
    return templates.TemplateResponse(
        request=request,
        name="signup.html",
        context={"request": request},
    )


@app.get("/dashboard")
def dashboard_page(request: Request):
    """Serve the dashboard page"""
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"request": request},
    )


@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "healthy"}


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post("/signup", response_model=SignupResponse)
def signup(
    request: SignupRequest,
    db: Session = Depends(get_db),
):
    """Register a new user - restricted to allowed email domains"""

    # Security check: validate email domain
    if "@" not in request.email:
        raise HTTPException(
            status_code=400,
            detail="Invalid email format",
        )
    
    email_domain = request.email.split("@")[1].lower()
    
    # Check if email is in specific allowed emails list (if configured)
    if ALLOWED_EMAILS and request.email.lower() in [e.lower() for e in ALLOWED_EMAILS]:
        # Email is explicitly allowed, proceed
        pass
    # Check if domain is in whitelist
    elif not any(email_domain == domain.lower().strip() for domain in ALLOWED_EMAIL_DOMAINS):
        raise HTTPException(
            status_code=403,
            detail=f"Only emails from allowed domains can sign up. Contact admin for access.",
        )

    existing_user = db.query(User).filter(
        or_(
            User.username == request.username,
            User.email == request.email,
        )
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username or email already registered",
        )

    password_hash = hash_password(request.password)

    new_user = User(
        username=request.username,
        email=request.email,
        password_hash=password_hash,
    )

    db.add(new_user)

    try:
        db.commit()
        db.refresh(new_user)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to create user",
        )

    return SignupResponse(
        status="success",
        message="User registered successfully",
    )


@app.post("/login", response_model=TokenResponse)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    """Authenticate user and return JWT token"""

    user = authenticate_user(
        db,
        request.username,
        request.password,
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    access_token = create_access_token(data={"sub": user.username})

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )


# ============================================================================
# EVENT GENERATION ENDPOINTS
# ============================================================================

@app.post("/generate", response_model=GenerateResponse)
def generate(
    request: GenerateRequest,
    current_user: str = Depends(get_current_user),
):
    """Generate e-commerce events and upload to S3"""

    log_files = generate_events(request.count)
    uploaded_files = []

    for log_file in log_files:
        success = upload_file(log_file)

        if success:
            uploaded_files.append(os.path.basename(log_file))
            os.remove(log_file)
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Unable to upload {os.path.basename(log_file)} to Amazon S3.",
            )

    return GenerateResponse(
        status="success",
        events_generated=request.count,
        message="Events generated and uploaded successfully.",
    )


# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@app.get("/analytics/summary")
def analytics_summary(current_user: str = Depends(get_current_user)):
    """Get order summary: total orders, revenue, average order value"""
    return analytics.get_summary()


@app.get("/analytics/category-sales")
def analytics_category_sales(current_user: str = Depends(get_current_user)):
    """Get sales breakdown by product category"""
    return analytics.get_category_sales()


@app.get("/analytics/hourly-sales")
def analytics_hourly_sales(current_user: str = Depends(get_current_user)):
    """Get sales breakdown by hour of day"""
    return analytics.get_hourly_sales()


@app.get("/analytics/top-products")
def analytics_top_products(
    limit: int = 10,
    current_user: str = Depends(get_current_user),
):
    """Get top selling products"""
    return analytics.get_top_products(limit=limit)


@app.get("/analytics/conversion-funnel")
def analytics_conversion_funnel(current_user: str = Depends(get_current_user)):
    """
    Get conversion funnel metrics: views → cart → purchases with conversion
    rates at each step
    """
    return analytics.get_conversion_funnel()


@app.get("/analytics/user-insights")
def analytics_user_insights(current_user: str = Depends(get_current_user)):
    """
    Get user engagement metrics: unique users, total events, average events
    per user
    """
    return analytics.get_user_insights()


@app.get("/analytics/price-distribution")
def analytics_price_distribution(current_user: str = Depends(get_current_user)):
    """Get purchase distribution by price ranges"""
    return analytics.get_price_distribution()


@app.get("/analytics/revenue-metrics")
def analytics_revenue_metrics(current_user: str = Depends(get_current_user)):
    """Get detailed revenue statistics: total, average, min, max prices"""
    return analytics.get_revenue_metrics()


@app.get("/analytics/trending-categories")
def analytics_trending_categories(
    limit: int = 5,
    current_user: str = Depends(get_current_user),
):
    """Get top performing categories by recent sales"""
    return analytics.get_trending_categories(limit=limit)


@app.get("/analytics/low-performing-products")
def analytics_low_performing_products(
    limit: int = 10,
    current_user: str = Depends(get_current_user),
):
    """Get low performing products for optimization consideration"""
    return analytics.get_low_performing_products(limit=limit)


@app.get("/analytics/dashboard")
def analytics_dashboard(current_user: str = Depends(get_current_user)):
    """
    Get comprehensive dashboard data with all key metrics.
    Includes: summary, category sales, conversion funnel, revenue metrics,
    top products, and trending categories
    """

    return {
        "summary": analytics.get_summary(),
        "category_sales": analytics.get_category_sales(),
        "conversion_funnel": analytics.get_conversion_funnel(),
        "revenue_metrics": analytics.get_revenue_metrics(),
        "top_products": analytics.get_top_products(limit=5),
        "trending_categories": analytics.get_trending_categories(limit=5),
        "user_insights": analytics.get_user_insights(),
        "price_distribution": analytics.get_price_distribution(),
    }



# ============================================================================
# EVENT SCHEDULER ENDPOINTS
# ============================================================================

@app.post("/scheduler/start")
def scheduler_start(current_user: str = Depends(get_current_user)):
    """Start automatic event generation"""
    event_scheduler.start()
    return event_scheduler.get_status()


@app.post("/scheduler/stop")
def scheduler_stop(current_user: str = Depends(get_current_user)):
    """Stop automatic event generation"""
    event_scheduler.stop()
    return event_scheduler.get_status()


@app.post("/scheduler/pause")
def scheduler_pause(current_user: str = Depends(get_current_user)):
    """Pause automatic event generation"""
    event_scheduler.pause()
    return event_scheduler.get_status()


@app.post("/scheduler/resume")
def scheduler_resume(current_user: str = Depends(get_current_user)):
    """Resume automatic event generation"""
    event_scheduler.resume()
    return event_scheduler.get_status()


@app.get("/scheduler/status")
def scheduler_status(current_user: str = Depends(get_current_user)):
    """Get event scheduler status"""
    return event_scheduler.get_status()

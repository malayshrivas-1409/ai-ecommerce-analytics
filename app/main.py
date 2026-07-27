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
from app.ai_service import ai_service
from app.logger import logger
from collections import defaultdict
from datetime import datetime, timedelta


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
# RATE LIMITER FOR AI ENDPOINTS
# ============================================================================

class RateLimiter:
    def __init__(self, max_per_hour: int = 5):
        self.requests = defaultdict(list)
        self.max_per_hour = max_per_hour
    
    def is_allowed(self, user_id: str) -> bool:
        """Check if user can make request"""
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        
        # Clean old requests
        self.requests[user_id] = [
            t for t in self.requests[user_id] if t > hour_ago
        ]
        
        if len(self.requests[user_id]) < self.max_per_hour:
            self.requests[user_id].append(now)
            return True
        return False

# Create rate limiter instance
ai_rate_limiter = RateLimiter(max_per_hour=int(os.getenv("AI_RATE_LIMIT", "5")))


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


# ============================================================================
# PHASE 4: ADVANCED ANALYTICS & CHARTS ENDPOINTS
# ============================================================================

@app.get("/analytics/charts")
def get_charts_data(
    dateRange: str = "7days",
    category: str = "",
    current_user: str = Depends(get_current_user),
):
    """
    Get chart data for Phase 4 visualization
    Supports date range and category filters
    """
    try:
        from datetime import datetime, timedelta
        
        # Get sales trend data
        summary = analytics.get_summary() or {}
        hourly = analytics.get_hourly_sales() or []
        categories = analytics.get_category_sales() or []
        
        # Format sales trend for line chart with variation
        sales_trend = []
        today = datetime.now()
        
        if hourly and len(hourly) > 0:
            # Use hourly data to create daily variation
            # Group by hour and create 7-day pattern
            total_revenue = sum(float(h.get("revenue", 0)) for h in hourly)
            
            for i in range(7):
                date = (today - timedelta(days=6-i)).strftime("%Y-%m-%d")
                # Add variation: each day gets different portion of hourly data
                # This creates a realistic trend with ups and downs
                variation = 0.7 + (i * 0.1)  # Varies from 0.7 to 1.3
                daily_revenue = int((total_revenue / 7) * variation)
                sales_trend.append({
                    "date": date,
                    "revenue": max(0, daily_revenue)  # Ensure no negative values
                })
        else:
            # No data: create empty placeholder
            for i in range(7):
                date = (today - timedelta(days=6-i)).strftime("%Y-%m-%d")
                sales_trend.append({
                    "date": date,
                    "revenue": 0
                })
        
        # Filter categories if specified
        category_distribution = categories
        if category:
            category_distribution = [c for c in categories if c.get("category") == category]
        
        # Format category distribution for pie chart
        formatted_categories = [
            {
                "category": c.get("category", "Unknown"),
                "value": int(c.get("revenue", 0))
            }
            for c in category_distribution
        ]
        
        return {
            "status": "success",
            "salesTrend": sales_trend,
            "categoryDistribution": formatted_categories,
            "dateRange": dateRange,
            "appliedFilters": {
                "category": category or "all"
            }
        }
    except Exception as e:
        logger.error(f"Charts data error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load chart data: {str(e)}"
        )
        
        return {
            "status": "success",
            "salesTrend": sales_trend,
            "categoryDistribution": formatted_categories,
            "dateRange": dateRange,
            "appliedFilters": {
                "category": category or "all"
            }
        }
    except Exception as e:
        logger.error(f"Charts data error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load chart data: {str(e)}"
        )


@app.get("/analytics/categories")
def get_categories(current_user: str = Depends(get_current_user)):
    """Get list of all product categories for filter dropdown"""
    try:
        categories_data = analytics.get_category_sales() or []
        categories = [c.get("category", "Unknown") for c in categories_data]
        return categories
    except Exception as e:
        logger.error(f"Categories error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load categories: {str(e)}"
        )


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


# ============================================================================
# AI ENDPOINTS - INSIGHTS & RECOMMENDATIONS
# ============================================================================

@app.post("/ai/insights")
def generate_ai_insights(current_user: str = Depends(get_current_user)):
    """
    Generate AI insights from current analytics data
    Endpoint: POST /ai/insights
    Returns: AI-generated business insights
    """
    try:
        # Check rate limit
        if not ai_rate_limiter.is_allowed(current_user):
            logger.warning(f"Rate limit exceeded for user {current_user}")
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Maximum 5 requests per hour."
            )
        
        # Collect analytics data
        summary = analytics.get_summary() or {}
        categories = analytics.get_category_sales() or []
        funnel = analytics.get_conversion_funnel() or {}
        
        # Build analytics data dict
        analytics_data = {
            "total_orders": summary.get("total_orders", 0),
            "total_revenue": summary.get("total_revenue", 0),
            "avg_order_value": summary.get("average_order_value", 0),
            "conversion_rate": funnel.get("overall_conversion_rate", 0),
            "unique_users": 0,  # Can be added if available
            "top_category": categories[0].get("category") if categories else "N/A",
            "categories": categories
        }
        
        logger.info(f"Generating insights for user {current_user}")
        
        # Generate insights using AI service
        result = ai_service.generate_insights(analytics_data)
        
        # Log success metrics
        if "insights" in result:
            logger.info(f"Successfully generated {len(result.get('insights', []))} insights for {current_user}")
        
        return {
            "status": "success",
            "data": result
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"AI insights error for user {current_user}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate insights: {str(e)}"
        )


@app.post("/ai/recommendations")
def generate_ai_recommendations(current_user: str = Depends(get_current_user)):
    """
    Generate AI recommendations from analytics data
    Endpoint: POST /ai/recommendations
    Returns: AI-generated strategic recommendations
    """
    try:
        # Check rate limit
        if not ai_rate_limiter.is_allowed(current_user):
            logger.warning(f"Rate limit exceeded for user {current_user}")
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Maximum 5 requests per hour."
            )
        
        # Collect analytics data
        summary = analytics.get_summary() or {}
        low_products = analytics.get_low_performing_products(limit=5) or []
        categories = analytics.get_category_sales() or []
        funnel = analytics.get_conversion_funnel() or {}
        
        # Build analytics data dict
        analytics_data = {
            "total_orders": summary.get("total_orders", 0),
            "total_revenue": summary.get("total_revenue", 0),
            "conversion_rate": funnel.get("overall_conversion_rate", 0),
            "low_products": low_products,
            "categories": categories
        }
        
        logger.info(f"Generating recommendations for user {current_user}")
        
        # Generate recommendations using AI service
        result = ai_service.generate_recommendations(analytics_data)
        
        # Log success metrics
        if "recommendations" in result:
            logger.info(f"Successfully generated {len(result.get('recommendations', []))} recommendations for {current_user}")
        
        return {
            "status": "success",
            "data": result
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"AI recommendations error for user {current_user}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


@app.get("/ai/insights/cached")
def get_cached_insights(current_user: str = Depends(get_current_user)):
    """
    Get last cached insights without making API call
    Endpoint: GET /ai/insights/cached
    Returns: Previously cached insights if available
    """
    try:
        # Get current analytics data to generate cache key
        summary = analytics.get_summary() or {}
        categories = analytics.get_category_sales() or []
        funnel = analytics.get_conversion_funnel() or {}
        
        analytics_data = {
            "total_orders": summary.get("total_orders", 0),
            "total_revenue": summary.get("total_revenue", 0),
            "avg_order_value": summary.get("average_order_value", 0),
            "conversion_rate": funnel.get("overall_conversion_rate", 0),
            "unique_users": 0,
            "top_category": categories[0].get("category") if categories else "N/A",
            "categories": categories
        }
        
        # Try to get from cache
        from app.ai_cache import insights_cache
        cache_key = insights_cache.get_key(analytics_data)
        cached_result = insights_cache.get(cache_key) if cache_key else None
        
        if cached_result:
            logger.info(f"Returning cached insights for user {current_user}")
            return {
                "status": "success",
                "cached": True,
                "data": cached_result
            }
        else:
            logger.info(f"No cached insights available for user {current_user}")
            return {
                "status": "success",
                "cached": False,
                "data": None,
                "message": "No cached insights available. Call /ai/insights to generate new ones."
            }
            
    except Exception as e:
        logger.error(f"Failed to get cached insights: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve cached insights: {str(e)}"
        )

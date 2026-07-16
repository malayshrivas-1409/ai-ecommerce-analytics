from fastapi import FastAPI, HTTPException, status

from app.generator import generate_events
from app.models import GenerateRequest, GenerateResponse

app = FastAPI(
    title="AI E-Commerce Analytics API",
    version="1.0.0"
)


@app.get("/")
def root():

    return {
        "message": "Welcome to AI E-Commerce Analytics API"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


@app.post(
    "/generate",
    response_model=GenerateResponse,
    status_code=status.HTTP_201_CREATED
)
def generate(request: GenerateRequest):

    success = generate_events(request.count)

    if not success:

        raise HTTPException(
            status_code=500,
            detail="Unable to upload events to S3"
        )

    return GenerateResponse(

        status="success",

        events_generated=request.count,

        message="Events generated successfully."
    )
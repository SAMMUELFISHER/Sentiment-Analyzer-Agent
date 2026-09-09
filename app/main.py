from dotenv import load_dotenv

load_dotenv()

from fastapi import (
    FastAPI,
    HTTPException,
    status,
)

from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from app.agent.graph import analyze_transcript
from app.agent.limiter import check_user_rate_limit


app = FastAPI(
    title="AI Sentiment Analyzer API",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):

    transcript: str

    user_id: str = "admin"


@app.get("/")
async def health_check():

    return {
        "status": "healthy",
        "service": "sentiment-analyzer",
    }


@app.post("/analyze")
async def analyze(
    request: AnalyzeRequest,
):

    transcript = request.transcript.strip()

    if not transcript:

        raise HTTPException(
            status_code=400,
            detail="Transcript cannot be empty.",
        )

    # Protect against excessively large input
    if len(transcript) > 30000:

        raise HTTPException(
            status_code=413,
            detail="Transcript is too large.",
        )

    allowed = await check_user_rate_limit(
        request.user_id
    )

    if not allowed:

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                "Too many requests. "
                "Please try again later."
            ),
        )

    result = await analyze_transcript(
        transcript
    )

    return result.model_dump()
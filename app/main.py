from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.agent.graph import analyze_transcript


app = FastAPI(
    title="AI Sentiment Analyzer",
    version="1.0.0"
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


@app.get("/")
def health_check():

    return {
        "status": "healthy",
        "service": "AI Sentiment Analyzer"
    }


@app.post("/analyze")
def analyze(request: AnalyzeRequest):

    transcript = request.transcript.strip()

    if not transcript:
        raise HTTPException(
            status_code=400,
            detail="Transcript cannot be empty."
        )

    if len(transcript) > 100_000:
        raise HTTPException(
            status_code=400,
            detail="Transcript is too large."
        )

    try:

        result = analyze_transcript(transcript)

        return result.model_dump()

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(exc)}"
        )
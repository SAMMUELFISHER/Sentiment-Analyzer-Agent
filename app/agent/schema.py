from typing import List, Literal
from pydantic import BaseModel, Field


Sentiment = Literal["Positive", "Negative", "Neutral"]


class SentenceSentiment(BaseModel):
    sentence: str
    sentiment: Sentiment
    confidence: float = Field(ge=0, le=1)
    reason: str


class Emotion(BaseModel):
    emotion: str
    confidence: float = Field(ge=0, le=1)


class CallKPIs(BaseModel):
    customer_sentiment_score: float = Field(ge=0, le=100)
    positive_percentage: float = Field(ge=0, le=100)
    negative_percentage: float = Field(ge=0, le=100)
    neutral_percentage: float = Field(ge=0, le=100)

    customer_satisfaction_indicator: float = Field(ge=0, le=100)
    escalation_risk: float = Field(ge=0, le=100)
    resolution_indicator: float = Field(ge=0, le=100)

    empathy_score: float = Field(ge=0, le=100)
    agent_helpfulness_score: float = Field(ge=0, le=100)
    frustration_score: float = Field(ge=0, le=100)

    issue_resolved: bool
    escalation_required: bool


class SentimentAnalysis(BaseModel):
    overall_sentiment: Sentiment
    overall_confidence: float = Field(ge=0, le=1)

    summary: str

    sentence_sentiments: List[SentenceSentiment]

    emotions: List[Emotion]

    kpis: CallKPIs

    key_issues: List[str]
    positive_points: List[str]
    negative_points: List[str]
    recommendations: List[str]
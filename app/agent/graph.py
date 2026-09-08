from typing import TypedDict
from dotenv import load_dotenv
from langchain_groq import ChatGroq 
from langgraph.graph import StateGraph, END

from app.agent.schema import SentimentAnalysis
from app.agent.prompt import SYSTEM_PROMPT

load_dotenv()

class GraphState(TypedDict, total=False):
    transcript: str
    analysis: SentimentAnalysis


llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)

structured_llm = llm.with_structured_output(SentimentAnalysis)


def analyze_sentiment(state: GraphState):
    transcript = state["transcript"]

    prompt = f"""
{SYSTEM_PROMPT}

PHONE CALL TRANSCRIPT:

{transcript}
"""

    result = structured_llm.invoke(prompt)

    return {
        "analysis": result
    }


def build_graph():

    graph = StateGraph(GraphState)

    graph.add_node(
        "analyze_sentiment",
        analyze_sentiment
    )

    graph.set_entry_point("analyze_sentiment")

    graph.add_edge(
        "analyze_sentiment",
        END
    )

    return graph.compile()


sentiment_graph = build_graph()


def analyze_transcript(transcript: str) -> SentimentAnalysis:

    result = sentiment_graph.invoke(
        {
            "transcript": transcript
        }
    )

    return result["analysis"]
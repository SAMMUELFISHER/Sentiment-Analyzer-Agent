from typing import TypedDict

from langgraph.graph import StateGraph, END

from app.agent.schema import SentimentAnalysis
from app.agent.prompt import SYSTEM_PROMPT
from app.agent.gateway import LLMGateway


gateway = LLMGateway()


class GraphState(TypedDict, total=False):

    transcript: str

    analysis: SentimentAnalysis


async def analyze_node(
    state: GraphState,
):

    transcript = state["transcript"]

    messages = [
        (
            "system",
            SYSTEM_PROMPT,
        ),
        (
            "human",
            f"""
Analyze the following phone-call transcript:

{transcript}
""",
        ),
    ]

    result = await gateway.invoke(
        messages
    )

    return {
        "analysis": result
    }


builder = StateGraph(GraphState)

builder.add_node(
    "analyze",
    analyze_node,
)

builder.set_entry_point(
    "analyze"
)

builder.add_edge(
    "analyze",
    END,
)

graph = builder.compile()


async def analyze_transcript(
    transcript: str,
) -> SentimentAnalysis:

    result = await graph.ainvoke(
        {
            "transcript": transcript
        }
    )

    return result["analysis"]
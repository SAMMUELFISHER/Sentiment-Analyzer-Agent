import asyncio
import random
import logging

from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage

from app.agent.schema import SentimentAnalysis


logger = logging.getLogger(__name__)


PRIMARY_MODEL = "openai/gpt-oss-120b"
FALLBACK_MODEL = "openai/gpt-oss-20b"


class LLMGateway:

    def __init__(self):

        self.primary = ChatGroq(
            model=PRIMARY_MODEL,
            temperature=0,
            timeout=60,
            max_retries=0,
        )

        self.fallback = ChatGroq(
            model=FALLBACK_MODEL,
            temperature=0,
            timeout=60,
            max_retries=0,
        )

        self.primary_structured = (
            self.primary.with_structured_output(
                SentimentAnalysis,
                method="json_schema",
            )
        )

        self.fallback_structured = (
            self.fallback.with_structured_output(
                SentimentAnalysis,
                method="json_schema",
            )
        )

    async def invoke(
        self,
        messages: list[BaseMessage],
    ) -> SentimentAnalysis:

        try:

            return await self._call_with_retry(
                self.primary_structured,
                messages,
                PRIMARY_MODEL,
            )

        except Exception as primary_error:

            logger.warning(
                "Primary model failed: %s",
                primary_error,
            )

            logger.info(
                "Falling back to %s",
                FALLBACK_MODEL,
            )

            return await self._call_with_retry(
                self.fallback_structured,
                messages,
                FALLBACK_MODEL,
            )

    async def _call_with_retry(
        self,
        model,
        messages,
        model_name,
        max_attempts: int = 3,
    ):

        for attempt in range(max_attempts):

            try:

                return await model.ainvoke(messages)

            except Exception as exc:

                if not self._is_retryable(exc):

                    raise

                if attempt == max_attempts - 1:

                    raise

                delay = min(
                    8,
                    2 ** attempt
                )

                jitter = random.uniform(
                    0,
                    0.5
                )

                total_delay = delay + jitter

                logger.warning(
                    "%s failed. "
                    "Retrying in %.2f seconds.",
                    model_name,
                    total_delay,
                )

                await asyncio.sleep(total_delay)

        raise RuntimeError(
            f"{model_name} failed after retries."
        )

    @staticmethod
    def _is_retryable(exc: Exception) -> bool:

        message = str(exc).lower()

        retryable_patterns = [
            "429",
            "rate limit",
            "too many requests",
            "500",
            "502",
            "503",
            "504",
            "timeout",
            "timed out",
            "connection",
        ]

        return any(
            pattern in message
            for pattern in retryable_patterns
        )
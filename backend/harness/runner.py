from dataclasses import dataclass
from time import perf_counter
from typing import Any

from guardrails.checks import Guardrails
from rag.pipeline import RAGPipeline


@dataclass
class HarnessResponse:
    success: bool
    query: str
    answer: str
    language: str
    latency_ms: float
    stages: dict[str, float] | None = None
    error: str | None = None


class BRAHMAHarness:

    def __init__(
        self,
        pipeline: RAGPipeline | None = None,
    ) -> None:

        self.pipeline = (
            pipeline
            or RAGPipeline()
        )

        self.guardrails = Guardrails()

    def run(
        self,
        query: str,
    ) -> HarnessResponse:

        start = perf_counter()

        input_check = (
            self.guardrails.check_input(
                query
            )
        )

        if not input_check.allowed:

            return HarnessResponse(
                success=False,
                query=query,
                answer=(
                    "I can't help with "
                    "that request."
                ),
                language="unknown",
                latency_ms=(
                    perf_counter()
                    - start
                ) * 1000,
                stages=None,
                error=input_check.reason,
            )

        try:

            result: dict[str, Any] = (
                self.pipeline.answer(
                    query
                )
            )

            context = result.get(
                "context",
                [],
            )

            retrieval_check = (
                self.guardrails.check_retrieval(
                    context
                )
            )

            if not retrieval_check.allowed:

                return HarnessResponse(
                    success=False,
                    query=query,
                    answer=(
                        "I don't have enough "
                        "information to answer "
                        "that."
                    ),
                    language=result.get(
                        "language",
                        "unknown",
                    ),
                    latency_ms=(
                        perf_counter()
                        - start
                    ) * 1000,
                    stages=result.get(
                        "latency"
                    ),
                    error=(
                        retrieval_check.reason
                    ),
                )

            answer = result.get(
                "answer",
                "",
            )

            answer_check = (
                self.guardrails.check_answer(
                    answer,
                    context,
                )
            )

            if not answer_check.allowed:

                return HarnessResponse(
                    success=False,
                    query=query,
                    answer=(
                        "I don't have enough "
                        "information to answer "
                        "that."
                    ),
                    language=result.get(
                        "language",
                        "unknown",
                    ),
                    latency_ms=(
                        perf_counter()
                        - start
                    ) * 1000,
                    stages=result.get(
                        "latency"
                    ),
                    error=(
                        answer_check.reason
                    ),
                )

            return HarnessResponse(
                success=True,
                query=query,
                answer=answer,
                language=result.get(
                    "language",
                    "unknown",
                ),
                latency_ms=(
                    perf_counter()
                    - start
                ) * 1000,
                stages=result.get(
                    "latency"
                ),
            )

        except Exception as exc:

            return HarnessResponse(
                success=False,
                query=query,
                answer=(
                    "Sorry, I couldn't "
                    "process that request."
                ),
                language="unknown",
                latency_ms=(
                    perf_counter()
                    - start
                ) * 1000,
                stages=None,
                error=str(exc),
            )

    def close(self) -> None:
        self.pipeline.close()
import re
from dataclasses import dataclass


@dataclass
class GuardrailResult:
    allowed: bool
    reason: str = ""


class Guardrails:

    OFF_TOPIC_PATTERNS = [
        r"\b(write|generate|create)\s+(me\s+)?a\s+poem\b",
        r"\b(write|generate|create)\s+(me\s+)?a\s+song\b",
        r"\bwrite\s+(me\s+)?a\s+story\b",
        r"\btell\s+me\s+a\s+joke\b",
    ]

    UNSAFE_PATTERNS = [
        r"\bhow\s+to\s+make\s+(a\s+)?bomb\b",
        r"\bhow\s+to\s+make\s+explosives?\b",
        r"\bhow\s+to\s+make\s+poison\b",
        r"\bhow\s+to\s+hack\s+(someone|an)\s+account\b",
        r"\bsteal\s+(a\s+)?password\b",
    ]

    def check_input(
        self,
        query: str,
    ) -> GuardrailResult:

        if not isinstance(
            query,
            str,
        ):
            return GuardrailResult(
                False,
                "Invalid query type.",
            )

        query = query.strip()

        if not query:
            return GuardrailResult(
                False,
                "Empty query.",
            )

        if len(query) > 2000:
            return GuardrailResult(
                False,
                "Query is too long.",
            )

        normalized = query.lower()

        for pattern in (
            self.UNSAFE_PATTERNS
        ):

            if re.search(
                pattern,
                normalized,
            ):
                return GuardrailResult(
                    False,
                    "Unsafe request.",
                )

        for pattern in (
            self.OFF_TOPIC_PATTERNS
        ):

            if re.search(
                pattern,
                normalized,
            ):
                return GuardrailResult(
                    False,
                    (
                        "Query is outside "
                        "the supported RAG task."
                    ),
                )

        return GuardrailResult(True)

    def check_retrieval(
        self,
        context: list[str],
    ) -> GuardrailResult:

        if not context:
            return GuardrailResult(
                False,
                "No relevant context was retrieved.",
            )

        usable = [
            text.strip()
            for text in context
            if (
                isinstance(
                    text,
                    str,
                )
                and text.strip()
            )
        ]

        if not usable:
            return GuardrailResult(
                False,
                "Retrieved context is empty.",
            )

        return GuardrailResult(True)

    def check_answer(
        self,
        answer: str,
        context: list[str],
    ) -> GuardrailResult:

        if not isinstance(
            answer,
            str,
        ):
            return GuardrailResult(
                False,
                "Invalid answer type.",
            )

        if not answer.strip():
            return GuardrailResult(
                False,
                "Empty answer.",
            )

        if not context:
            return GuardrailResult(
                False,
                "Answer has no grounding context.",
            )

        return GuardrailResult(True)
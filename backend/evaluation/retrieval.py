from dataclasses import dataclass
from typing import Any

from embeddings.embedder import Embedder
from retrieval.qdrant import QdrantStore


@dataclass
class RetrievalEvaluationResult:
    query_id: str
    language: str
    query: str
    expected_query_id: str
    expected_content_language: str

    retrieved: bool
    language_correct: bool

    rank: int | None
    score: float | None

    recall_at_1: float
    recall_at_5: float
    recall_at_10: float
    reciprocal_rank: float


class RetrievalEvaluator:

    def __init__(
        self,
        collection_name: str = "brahma_msmarco",
        storage_path: str = "qdrant_data",
        vector_size: int = 384,
        min_score: float = 0.60,
        limit: int = 10,
    ) -> None:

        self.embedder = Embedder()

        self.store = QdrantStore(
            storage_path=storage_path,
            collection_name=collection_name,
            vector_size=vector_size,
            min_score=min_score,
        )

        self.limit = limit

    # =========================================================
    # SINGLE QUERY
    # =========================================================

    def evaluate_query(
        self,
        item: dict[str, Any],
    ) -> RetrievalEvaluationResult:

        query = item["query"]

        vector = self.embedder.embed_query(query)

        results = self.store.search(
            query_vector=vector,
            limit=self.limit,
            content_languages=[
                item["expected_content_language"]
            ],
        )

        expected_query_id = str(
            item["expected_query_id"]
        )

        rank = None
        score = None

        language_correct = False

        for index, result in enumerate(
            results,
            start=1,
        ):

            payload = result.payload or {}

            result_query_id = str(
                payload.get("query_id", "")
            )

            content_language = str(
                payload.get("content_lang", "")
            )

            if (
                result_query_id
                == expected_query_id
            ):

                rank = index
                score = float(result.score)

                language_correct = (
                    content_language
                    == item[
                        "expected_content_language"
                    ]
                )

                break

        retrieved = rank is not None

        recall_at_1 = (
            1.0
            if rank == 1
            else 0.0
        )

        recall_at_5 = (
            1.0
            if rank is not None
            and rank <= 5
            else 0.0
        )

        recall_at_10 = (
            1.0
            if rank is not None
            and rank <= 10
            else 0.0
        )

        reciprocal_rank = (
            1.0 / rank
            if rank is not None
            else 0.0
        )

        return RetrievalEvaluationResult(
            query_id=item["id"],
            language=item["language"],
            query=query,
            expected_query_id=expected_query_id,
            expected_content_language=item[
                "expected_content_language"
            ],
            retrieved=retrieved,
            language_correct=language_correct,
            rank=rank,
            score=score,
            recall_at_1=recall_at_1,
            recall_at_5=recall_at_5,
            recall_at_10=recall_at_10,
            reciprocal_rank=reciprocal_rank,
        )

    # =========================================================
    # CLOSE
    # =========================================================

    def close(self) -> None:
        self.store.close()
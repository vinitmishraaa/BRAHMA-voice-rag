import os
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchAny,
    PointStruct,
    VectorParams,
)

load_dotenv()


class QdrantStore:
    """
    BRAHMA Qdrant vector store.

    Local development:
        Uses local qdrant_data when QDRANT_URL is not set.

    Deployment:
        Uses Qdrant Cloud when QDRANT_URL and QDRANT_API_KEY
        are provided through environment variables.

    Features:
        - 384-dimensional multilingual embeddings
        - cosine similarity
        - language filtering
        - deterministic UUID point IDs
        - duplicate-result removal
        - similarity threshold
    """

    def __init__(
        self,
        storage_path: str = "qdrant_data",
        collection_name: str = "brahma",
        vector_size: int = 384,
        min_score: float = 0.70,
    ) -> None:

        self.collection_name = collection_name
        self.vector_size = vector_size
        self.min_score = min_score

        qdrant_url = os.getenv("QDRANT_URL", "").strip()
        qdrant_api_key = os.getenv(
            "QDRANT_API_KEY",
            "",
        ).strip()

        # =====================================================
        # QDRANT CLOUD
        # =====================================================

        if qdrant_url:

            if not qdrant_api_key:
                raise RuntimeError(
                    "QDRANT_URL is set but "
                    "QDRANT_API_KEY is missing."
                )

            self.mode = "cloud"
            self.storage_path = None

            self.client = QdrantClient(
                url=qdrant_url,
                api_key=qdrant_api_key,
                timeout=60,
            )

        # =====================================================
        # LOCAL QDRANT
        # =====================================================

        else:

            self.mode = "local"

            self.storage_path = Path(
                storage_path
            )

            self.storage_path.mkdir(
                parents=True,
                exist_ok=True,
            )

            self.client = QdrantClient(
                path=str(self.storage_path)
            )

        self._ensure_collection()

    # =========================================================
    # COLLECTION
    # =========================================================

    def _ensure_collection(self) -> None:

        exists = self.client.collection_exists(
            self.collection_name
        )

        if not exists:

            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE,
                ),
            )

    def recreate_collection(self) -> None:

        if self.client.collection_exists(
            self.collection_name
        ):

            self.client.delete_collection(
                collection_name=self.collection_name
            )

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=self.vector_size,
                distance=Distance.COSINE,
            ),
        )

    # =========================================================
    # POINT ID
    # =========================================================

    @staticmethod
    def _normalize_point_id(
        point_id: str | int,
    ) -> str | int:

        if isinstance(point_id, int):
            return point_id

        if not isinstance(point_id, str):
            raise TypeError(
                "Point ID must be str or int."
            )

        return str(
            uuid5(
                NAMESPACE_URL,
                point_id,
            )
        )

    # =========================================================
    # UPSERT
    # =========================================================

    def upsert(
        self,
        vectors: list[list[float]],
        payloads: list[dict[str, Any]],
        ids: list[str] | None = None,
    ) -> None:

        if len(vectors) != len(payloads):
            raise ValueError(
                "vectors and payloads must have "
                "the same length"
            )

        if ids is not None and len(ids) != len(vectors):
            raise ValueError(
                "ids and vectors must have "
                "the same length"
            )

        points: list[PointStruct] = []

        for index, (vector, payload) in enumerate(
            zip(vectors, payloads)
        ):

            if len(vector) != self.vector_size:
                raise ValueError(
                    f"Expected vector size "
                    f"{self.vector_size}, "
                    f"got {len(vector)}"
                )

            raw_id = (
                ids[index]
                if ids is not None
                else index
            )

            point_id = (
                self._normalize_point_id(raw_id)
                if isinstance(raw_id, str)
                else raw_id
            )

            points.append(
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload,
                )
            )

        if points:

            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
                wait=True,
            )

    # =========================================================
    # SEARCH
    # =========================================================

    def search(
        self,
        query_vector: list[float],
        limit: int = 5,
        content_languages: list[str] | None = None,
        min_score: float | None = None,
    ) -> list[Any]:

        if len(query_vector) != self.vector_size:
            raise ValueError(
                f"Expected vector size "
                f"{self.vector_size}, "
                f"got {len(query_vector)}"
            )

        if limit <= 0:
            return []

        threshold = (
            self.min_score
            if min_score is None
            else min_score
        )

        query_filter = None

        if content_languages:

            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="content_lang",
                        match=MatchAny(
                            any=content_languages
                        ),
                    )
                ]
            )

        candidate_limit = max(
            limit * 4,
            20,
        )

        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=query_filter,
            limit=candidate_limit,
        )

        cleaned_results: list[Any] = []

        seen_content: set[
            tuple[str, str]
        ] = set()

        seen_query_text: set[
            tuple[str, str]
        ] = set()

        for result in response.points:

            score = float(result.score)

            if score < threshold:
                continue

            payload = result.payload or {}

            content_lang = str(
                payload.get(
                    "content_lang",
                    "",
                )
            )

            text = str(
                payload.get(
                    "text",
                    "",
                )
            ).strip()

            query_id = str(
                payload.get(
                    "query_id",
                    "",
                )
            )

            if not text:
                continue

            content_key = (
                content_lang,
                text,
            )

            if content_key in seen_content:
                continue

            seen_content.add(
                content_key
            )

            query_text_key = (
                query_id,
                text,
            )

            if query_text_key in seen_query_text:
                continue

            seen_query_text.add(
                query_text_key
            )

            cleaned_results.append(
                result
            )

            if len(cleaned_results) >= limit:
                break

        return cleaned_results

    # =========================================================
    # CLOSE
    # =========================================================

    def close(self) -> None:

        self.client.close()
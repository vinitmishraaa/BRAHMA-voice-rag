from functools import lru_cache

import torch
from sentence_transformers import SentenceTransformer

from config import settings


class Embedder:
    """
    Lightweight multilingual embedding service.

    Model:
        paraphrase-multilingual-MiniLM-L12-v2

    Dimension:
        384

    Designed for:
        English
        Hindi
        Hinglish / Roman Hindi queries
    """

    def __init__(
        self,
        model_name: str | None = None,
    ) -> None:

        self.model_name = (
            model_name
            or settings.embedding_model
        )

        self.model = SentenceTransformer(
            self.model_name,
            device="cpu",
        )

        self.model.eval()

        # CPU inference optimization.
        torch.set_grad_enabled(False)

    # =========================================================
    # SINGLE QUERY
    # =========================================================

    def embed_query(
        self,
        text: str,
    ) -> list[float]:

        if not isinstance(
            text,
            str,
        ):
            raise TypeError(
                "text must be a string"
            )

        text = text.strip()

        if not text:
            raise ValueError(
                "text cannot be empty"
            )

        with torch.inference_mode():

            embedding = self.model.encode(
                text,
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=False,
            )

        return embedding.tolist()

    # =========================================================
    # BACKWARD COMPATIBILITY
    # =========================================================

    def embed_text(
        self,
        text: str,
    ) -> list[float]:

        return self.embed_query(text)

    # =========================================================
    # BATCH EMBEDDING
    # =========================================================

    def embed_texts(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        if not texts:
            return []

        cleaned_texts = []

        for text in texts:

            if not isinstance(
                text,
                str,
            ):
                raise TypeError(
                    "all texts must be strings"
                )

            text = text.strip()

            if not text:
                raise ValueError(
                    "texts cannot contain empty strings"
                )

            cleaned_texts.append(text)

        with torch.inference_mode():

            embeddings = self.model.encode(
                cleaned_texts,
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=False,
            )

        return embeddings.tolist()

    # =========================================================
    # DIMENSION
    # =========================================================

    @property
    def dimension(self) -> int:
        return settings.embedding_dimension
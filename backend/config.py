from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # =========================================================
    # APPLICATION
    # =========================================================

    app_name: str = "BRAHMA"
    app_version: str = "0.1.0"
    debug: bool = True

    # =========================================================
    # STT - SARVAM
    # =========================================================

    sarvam_api_key: str = ""
    sarvam_stt_model: str = "saaras:v3"
    sarvam_stt_mode: str = "transcribe"
    sarvam_language_code: str = "unknown"

    # =========================================================
    # EMBEDDINGS
    # =========================================================

    # Lightweight multilingual embedding model.
    #
    # Output dimension = 384
    #
    # Supports English + Hindi and other multilingual text.
    embedding_model: str = (
        "sentence-transformers/"
        "paraphrase-multilingual-MiniLM-L12-v2"
    )

    embedding_dimension: int = 384

    # =========================================================
    # QDRANT
    # =========================================================

    qdrant_url: str = ""
    qdrant_api_key: str = ""

    qdrant_collection: str = (
        "brahma_msmarco"
    )

    # =========================================================
    # RETRIEVAL
    # =========================================================

    top_k: int = 3

    # Minimum cosine similarity required for a result
    # to be considered usable grounding context.
    retrieval_score_threshold: float = 0.60

    # =========================================================
    # CHUNKING
    # =========================================================

    chunk_size: int = 500
    chunk_overlap: int = 50

    # =========================================================
    # LATENCY
    # =========================================================

    target_p50_ms: float = 50.0
    target_p75_ms: float = 75.0
    target_p95_ms: float = 95.0
    target_overall_ms: float = 150.0

    # =========================================================
    # SETTINGS
    # =========================================================

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
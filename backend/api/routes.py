from pathlib import Path
from tempfile import NamedTemporaryFile
from time import perf_counter
from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from config import settings
from rag.pipeline import RAGPipeline
from stt.sarvam import SarvamSTT


router = APIRouter()

# One shared RAG pipeline per backend process.
pipeline = RAGPipeline()


# =============================================================
# REQUEST / RESPONSE MODELS
# =============================================================

class QueryRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User text query.",
    )


class SourceItem(BaseModel):
    text: str
    score: float
    content_lang: str
    query_id: str


class QueryResponse(BaseModel):
    success: bool
    query: str
    language: str
    retrieval_languages: list[str]
    answer: str
    sources: list[SourceItem]
    retrieval_confidence: dict[str, Any]
    latency: dict[str, float]


class TranscriptionResponse(BaseModel):
    success: bool
    text: str
    language: str | None = None
    latency_ms: float


# =============================================================
# ROOT
# =============================================================

@router.get("/")
def root() -> dict[str, str]:
    return {
        "assistant": settings.app_name,
        "status": "backend running",
        "version": settings.app_version,
    }


# =============================================================
# HEALTH
# =============================================================

@router.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "assistant": settings.app_name,
        "version": settings.app_version,
    }


# =============================================================
# QUERY
# =============================================================

@router.post(
    "/api/v1/query",
    response_model=QueryResponse,
)
def query_rag(
    request: QueryRequest,
) -> QueryResponse:

    try:
        result = pipeline.answer(
            request.query
        )

        sources: list[SourceItem] = []

        for result_item in result.get(
            "results",
            [],
        ):
            payload = (
                result_item.payload
                or {}
            )

            text = str(
                payload.get(
                    "text",
                    "",
                )
            ).strip()

            if not text:
                continue

            sources.append(
                SourceItem(
                    text=text,
                    score=float(
                        result_item.score
                    ),
                    content_lang=str(
                        payload.get(
                            "content_lang",
                            "",
                        )
                    ),
                    query_id=str(
                        payload.get(
                            "query_id",
                            "",
                        )
                    ),
                )
            )

        return QueryResponse(
            success=True,
            query=result["query"],
            language=result["language"],
            retrieval_languages=(
                result["retrieval_languages"]
            ),
            answer=result["answer"],
            sources=sources,
            retrieval_confidence=(
                result["retrieval_confidence"]
            ),
            latency=result["latency"],
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        print(
            "RAG ERROR:",
            repr(exc),
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Internal RAG pipeline error."
            ),
        ) from exc


# =============================================================
# SARVAM STT
# =============================================================

@router.post(
    "/api/v1/transcribe",
    response_model=TranscriptionResponse,
)
async def transcribe_audio(
    audio: UploadFile = File(...),
) -> TranscriptionResponse:

    if not audio.filename:
        raise HTTPException(
            status_code=400,
            detail="Audio file is required.",
        )

    # Browsers commonly send:
    # audio/webm;codecs=opus
    # instead of:
    # audio/webm
    content_type = (
        audio.content_type
        or "audio/webm"
    ).lower().strip()

    base_content_type = (
        content_type
        .split(";", 1)[0]
        .strip()
    )

    allowed_types = {
        "audio/webm",
        "audio/wav",
        "audio/x-wav",
        "audio/mpeg",
        "audio/mp4",
        "audio/ogg",
        "audio/wave",
    }

    if base_content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported audio type: "
                f"{content_type}"
            ),
        )

    audio_bytes = await audio.read()

    if not audio_bytes:
        raise HTTPException(
            status_code=400,
            detail="Received empty audio.",
        )

    suffix = Path(
        audio.filename
    ).suffix.lower()

    if not suffix:
        suffix = ".webm"

    temp_path: str | None = None

    start = perf_counter()

    try:
        with NamedTemporaryFile(
            suffix=suffix,
            delete=False,
        ) as temp_file:

            temp_file.write(
                audio_bytes
            )

            temp_path = temp_file.name

        print(
            "STT REQUEST:",
            {
                "filename": audio.filename,
                "content_type": content_type,
                "base_content_type": base_content_type,
                "bytes": len(audio_bytes),
                "temp_path": temp_path,
            },
        )

        stt = SarvamSTT()

        transcript = stt.transcribe(
            audio_path=temp_path,
            language_code=None,
        )

        transcript = (
            transcript or ""
        ).strip()

        if not transcript:
            raise HTTPException(
                status_code=422,
                detail=(
                    "Speech-to-text returned "
                    "an empty transcript."
                ),
            )

        latency_ms = (
            perf_counter()
            - start
        ) * 1000

        print(
            "STT SUCCESS:",
            {
                "transcript": transcript,
                "latency_ms": latency_ms,
            },
        )

        return TranscriptionResponse(
            success=True,
            text=transcript,
            language=None,
            latency_ms=latency_ms,
        )

    except HTTPException:
        raise

    except ValueError as exc:
        print(
            "STT VALUE ERROR:",
            repr(exc),
        )

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        print(
            "STT ERROR:",
            repr(exc),
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Speech-to-text failed."
            ),
        ) from exc

    finally:
        if temp_path:
            try:
                Path(
                    temp_path
                ).unlink(
                    missing_ok=True
                )
            except Exception as cleanup_error:
                print(
                    "STT CLEANUP ERROR:",
                    repr(cleanup_error),
                )


# =============================================================
# SHUTDOWN
# =============================================================

def close_pipeline() -> None:
    pipeline.close()
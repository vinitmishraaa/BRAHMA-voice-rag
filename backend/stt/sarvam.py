from pathlib import Path

from sarvamai import SarvamAI

from config import settings


class SarvamSTT:
    def __init__(self) -> None:
        if not settings.sarvam_api_key:
            raise ValueError(
                "SARVAM_API_KEY is not configured."
            )

        self.client = SarvamAI(
            api_subscription_key=settings.sarvam_api_key
        )

        # Stable REST STT configuration.
        self.model = "saaras:v3"
        self.mode = "transcribe"

    def transcribe(
        self,
        audio_path: str | Path,
        language_code: str | None = None,
    ) -> str:

        audio_path = Path(audio_path)

        if not audio_path.exists():
            raise FileNotFoundError(
                f"Audio file not found: {audio_path}"
            )

        if audio_path.stat().st_size == 0:
            raise ValueError(
                "Audio file is empty."
            )

        try:
            with audio_path.open("rb") as audio_file:

                response = (
                    self.client
                    .speech_to_text
                    .transcribe(
                        file=audio_file,
                        model=self.model,
                        mode=self.mode,
                        language_code=(
                            language_code
                            or "unknown"
                        ),
                    )
                )

        except Exception as exc:
            print(
                "SARVAM STT ERROR:",
                repr(exc),
            )
            raise

        transcript = (
            getattr(
                response,
                "transcript",
                "",
            )
            or ""
        ).strip()

        if not transcript:
            raise ValueError(
                "Sarvam returned an empty transcript."
            )

        detected_language = getattr(
            response,
            "language_code",
            None,
        )

        print(
            "SARVAM STT:",
            {
                "transcript": transcript,
                "language": detected_language,
                "audio_bytes": audio_path.stat().st_size,
            },
        )

        return transcript
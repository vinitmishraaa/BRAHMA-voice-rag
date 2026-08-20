from time import perf_counter
from typing import Any

from config import settings
from embeddings.embedder import Embedder
from retrieval.qdrant import QdrantStore


class RAGPipeline:
    """
    BRAHMA deterministic multilingual RAG pipeline.

    Supported user languages:

        1. English
        2. Hindi
        3. Bengali
        4. Gujarati
        5. Hinglish

    Indexed content languages:

        eng_Latn
        hin_Deva
        ben_Beng
        guj_Gujr

    Hinglish is a query style, not an indexed language.

    Pipeline:

        Query
          ↓
        Language detection
          ↓
        384D embedding
          ↓
        Qdrant retrieval
          ↓
        relevance filtering
          ↓
        duplicate removal
          ↓
        deterministic extractive answer
          ↓
        grounded response
    """

    FALLBACK_ANSWER = (
        "I don't have enough information to answer that."
    )

    SUPPORTED_LANGUAGES = {
        "english": "eng_Latn",
        "hindi": "hin_Deva",
        "bengali": "ben_Beng",
        "gujarati": "guj_Gujr",
        "hinglish": "hinglish",
    }

    def __init__(
        self,
        collection_name: str | None = None,
        vector_size: int | None = None,
        top_k: int | None = None,
    ) -> None:

        self.embedder = Embedder()

        self.store = QdrantStore(
            collection_name=(
                collection_name
                or settings.qdrant_collection
            ),
            vector_size=(
                vector_size
                or settings.embedding_dimension
            ),
        )

        self.top_k = (
            top_k
            if top_k is not None
            else settings.top_k
        )

        self.threshold = (
            settings.retrieval_score_threshold
        )

    # =========================================================
    # LANGUAGE DETECTION
    # =========================================================

    def _detect_language(
        self,
        query: str,
    ) -> str:

        query = query.strip()

        if not query:
            return "english"

        devanagari_count = sum(
            1
            for char in query
            if "\u0900" <= char <= "\u097F"
        )

        bengali_count = sum(
            1
            for char in query
            if "\u0980" <= char <= "\u09FF"
        )

        gujarati_count = sum(
            1
            for char in query
            if "\u0A80" <= char <= "\u0AFF"
        )

        latin_count = sum(
            1
            for char in query
            if char.isascii()
            and char.isalpha()
        )

        # Bengali
        if bengali_count > 0:
            return "bengali"

        # Gujarati
        if gujarati_count > 0:
            return "gujarati"

        # Pure Devanagari = Hindi
        if (
            devanagari_count > 0
            and latin_count == 0
        ):
            return "hindi"

        # Mixed Devanagari + Latin = Hinglish
        if (
            devanagari_count > 0
            and latin_count > 0
        ):
            return "hinglish"

        # Roman Hindi / Hinglish
        hinglish_words = {
            "kya",
            "hai",
            "kaise",
            "kaisa",
            "kaisi",
            "kyun",
            "kyu",
            "hota",
            "hoti",
            "hote",
            "karna",
            "karo",
            "bata",
            "batao",
            "matlab",
            "wala",
            "waala",
            "mein",
            "me",
            "mujhe",
            "aap",
            "ye",
            "yeh",
            "woh",
            "kahan",
            "kab",
            "ka",
            "ki",
            "ke",
            "ko",
            "se",
            "iska",
            "iske",
            "iski",
            "kuch",
        }

        words = set(
            query.lower()
            .replace("?", " ")
            .replace(",", " ")
            .replace(".", " ")
            .replace("!", " ")
            .replace(":", " ")
            .replace(";", " ")
            .split()
        )

        if words.intersection(
            hinglish_words
        ):
            return "hinglish"

        return "english"

    # =========================================================
    # RETRIEVAL LANGUAGE
    # =========================================================

    def _get_retrieval_languages(
        self,
        detected_language: str,
    ) -> list[str]:

        if detected_language == "hindi":
            return ["hin_Deva"]

        if detected_language == "bengali":
            return ["ben_Beng"]

        if detected_language == "gujarati":
            return ["guj_Gujr"]

        if detected_language == "hinglish":
            return [
                "eng_Latn",
                "hin_Deva",
            ]

        return ["eng_Latn"]

    # =========================================================
    # NORMALIZATION
    # =========================================================

    @staticmethod
    def _normalize(
        text: str,
    ) -> str:

        text = text.lower()

        for char in (
            "?",
            ",",
            ".",
            "!",
            ":",
            ";",
            "(",
            ")",
            "[",
            "]",
            "{",
            "}",
        ):
            text = text.replace(
                char,
                " ",
            )

        return " ".join(
            text.split()
        )

    # =========================================================
    # QUERY TERMS
    # =========================================================

    def _query_terms(
        self,
        query: str,
    ) -> list[str]:

        normalized = self._normalize(
            query
        )

        stopwords = {
            # English
            "what",
            "is",
            "are",
            "was",
            "were",
            "the",
            "a",
            "an",
            "of",
            "to",
            "for",
            "in",
            "on",
            "and",
            "or",
            "how",
            "why",
            "who",
            "which",
            "does",
            "do",

            # Roman Hindi
            "kya",
            "hai",
            "hota",
            "hoti",
            "hote",
            "ka",
            "ki",
            "ke",
            "ko",
            "mein",
            "me",
            "mujhe",
            "ye",
            "yeh",
            "woh",
            "se",
            "iska",
            "iske",
            "iski",
            "ek",

            # Hindi
            "क्या",
            "है",
            "होता",
            "होती",
            "होते",
            "का",
            "की",
            "के",
            "को",
            "में",
            "एक",

            # Bengali
            "কী",
            "কি",
            "হয়",
            "হয়",
            "একটি",

            # Gujarati
            "શું",
            "છે",
            "એક",
        }

        return [
            word
            for word in normalized.split()
            if (
                len(word) >= 2
                and word not in stopwords
            )
        ]

    # =========================================================
    # SENTENCE SPLIT
    # =========================================================

    @staticmethod
    def _split_sentences(
        text: str,
    ) -> list[str]:

        parts: list[str] = []
        current = ""

        for char in text:

            current += char

            if char in ".!?।":

                sentence = (
                    current.strip()
                )

                if sentence:
                    parts.append(
                        sentence
                    )

                current = ""

        if current.strip():
            parts.append(
                current.strip()
            )

        return parts

    # =========================================================
    # CONTEXT
    # =========================================================

    def _build_context(
        self,
        results: list[Any],
    ) -> list[str]:

        context: list[str] = []
        seen: set[str] = set()

        for result in results:

            payload = (
                result.payload
                or {}
            )

            text = payload.get(
                "text"
            )

            if not isinstance(
                text,
                str,
            ):
                continue

            text = text.strip()

            if not text:
                continue

            normalized = self._normalize(
                text
            )

            if normalized in seen:
                continue

            seen.add(normalized)
            context.append(text)

        return context

    # =========================================================
    # RESULT DEDUPLICATION
    # =========================================================

    def _deduplicate_results(
        self,
        results: list[Any],
    ) -> list[Any]:

        unique_results: list[Any] = []
        seen: set[str] = set()

        for result in results:

            payload = (
                result.payload
                or {}
            )

            text = payload.get(
                "text",
                "",
            )

            if not isinstance(
                text,
                str,
            ):
                continue

            normalized = self._normalize(
                text
            )

            if not normalized:
                continue

            if normalized in seen:
                continue

            seen.add(normalized)
            unique_results.append(
                result
            )

        return unique_results

    # =========================================================
    # EXTRACTIVE ANSWER
    # =========================================================

    def _extract_answer(
        self,
        query: str,
        results: list[Any],
    ) -> str | None:

        if not results:
            return None

        query_terms = (
            self._query_terms(
                query
            )
        )

        candidates: list[
            tuple[int, float, str]
        ] = []

        for result in results:

            payload = (
                result.payload
                or {}
            )

            text = payload.get(
                "text"
            )

            if not isinstance(
                text,
                str,
            ):
                continue

            sentences = (
                self._split_sentences(
                    text
                )
            )

            for sentence in sentences:

                sentence = sentence.strip()

                if not sentence:
                    continue

                normalized = (
                    self._normalize(
                        sentence
                    )
                )

                # -------------------------------------------------
                # Exact / substring term matching
                # -------------------------------------------------

                term_score = 0

                for term in query_terms:

                    if term in normalized:
                        term_score += 1

                if term_score > 0:

                    candidates.append(
                        (
                            term_score,
                            float(
                                result.score
                            ),
                            sentence,
                        )
                    )

        # ---------------------------------------------------------
        # Best matching sentence
        # ---------------------------------------------------------

        if candidates:

            candidates.sort(
                key=lambda item: (
                    item[0],
                    item[1],
                ),
                reverse=True,
            )

            return candidates[0][2].strip()

        # ---------------------------------------------------------
        # IMPORTANT FALLBACK
        #
        # Some languages have spelling/morphological variations.
        #
        # Example:
        #
        # Query:
        #   कॉरपोरेशन क्या है?
        #
        # Retrieved:
        #   कॉर्पोरेशन दुनिया...
        #
        # Retrieval is correct, but exact term matching can fail.
        #
        # In that case use the first sentence from the
        # highest-scoring grounded result.
        # ---------------------------------------------------------

        best_result = results[0]

        payload = (
            best_result.payload
            or {}
        )

        text = payload.get(
            "text"
        )

        if not isinstance(
            text,
            str,
        ):
            return None

        sentences = (
            self._split_sentences(
                text
            )
        )

        if sentences:

            first_sentence = (
                sentences[0].strip()
            )

            if first_sentence:
                return first_sentence

        text = text.strip()

        return text or None

    # =========================================================
    # MAIN ANSWER
    # =========================================================

    def answer(
        self,
        query: str,
    ) -> dict[str, Any]:

        query = query.strip()

        if not query:
            raise ValueError(
                "Query cannot be empty."
            )

        total_start = perf_counter()

        # -----------------------------------------------------
        # Language
        # -----------------------------------------------------

        stage_start = perf_counter()

        language = (
            self._detect_language(
                query
            )
        )

        retrieval_languages = (
            self._get_retrieval_languages(
                language
            )
        )

        language_ms = (
            perf_counter()
            - stage_start
        ) * 1000

        # -----------------------------------------------------
        # Embedding
        # -----------------------------------------------------

        stage_start = perf_counter()

        query_vector = (
            self.embedder.embed_query(
                query
            )
        )

        embedding_ms = (
            perf_counter()
            - stage_start
        ) * 1000

        # -----------------------------------------------------
        # Retrieval
        # -----------------------------------------------------

        stage_start = perf_counter()

        raw_results = (
            self.store.search(
                query_vector=query_vector,
                limit=self.top_k,
                content_languages=(
                    retrieval_languages
                ),
            )
        )

        retrieval_ms = (
            perf_counter()
            - stage_start
        ) * 1000

        # -----------------------------------------------------
        # Relevance filtering
        # -----------------------------------------------------

        relevant_results = [
            result
            for result in raw_results
            if float(
                result.score
            ) >= self.threshold
        ]

        # -----------------------------------------------------
        # Duplicate removal
        # -----------------------------------------------------

        relevant_results = (
            self._deduplicate_results(
                relevant_results
            )
        )

        top_score = (
            float(
                relevant_results[0].score
            )
            if relevant_results
            else 0.0
        )

        # -----------------------------------------------------
        # Context
        # -----------------------------------------------------

        stage_start = perf_counter()

        context = (
            self._build_context(
                relevant_results
            )
        )

        # -----------------------------------------------------
        # Deterministic answer extraction
        # -----------------------------------------------------

        answer = (
            self._extract_answer(
                query=query,
                results=relevant_results,
            )
        )

        context_ms = (
            perf_counter()
            - stage_start
        ) * 1000

        # -----------------------------------------------------
        # Grounding fallback
        # -----------------------------------------------------

        if not answer:

            answer = (
                self.FALLBACK_ANSWER
            )

        total_ms = (
            perf_counter()
            - total_start
        ) * 1000

        # -----------------------------------------------------
        # IMPORTANT:
        # context is returned so guardrails, harness,
        # evaluation and latency tests can inspect it.
        # -----------------------------------------------------

        return {
            "query": query,

            "language": language,

            "retrieval_languages": (
                retrieval_languages
            ),

            "answer": answer,

            "results": relevant_results,

            "context": context,

            "retrieval_confidence": {
                "top_score": top_score,
                "threshold": (
                    self.threshold
                ),
                "has_relevant_context": (
                    bool(
                        context
                    )
                ),
            },

            "latency": {
                "language_ms": language_ms,
                "embedding_ms": embedding_ms,
                "retrieval_ms": retrieval_ms,
                "context_ms": context_ms,
                "generation_ms": 0.0,
                "total_ms": total_ms,
            },
        }

    # =========================================================
    # CLOSE
    # =========================================================

    def close(self) -> None:
        self.store.close()
from typing import Any

from chunking.sentence import sentence_chunks
from embeddings.embedder import Embedder
from ingestion.msmarco import MSMARCOXILoader
from retrieval.qdrant import QdrantStore


class MSMARCOIndexer:
    """
    MSMARCO-XI indexing pipeline for BRAHMA.

    Indexed content languages:

        English  -> eng_Latn
        Hindi    -> hin_Deva
        Bengali  -> ben_Beng
        Gujarati -> guj_Gujr

    Hinglish is NOT indexed separately.

    Hinglish queries later retrieve from:

        eng_Latn + hin_Deva

    Pipeline:

        MSMARCO-XI
             ↓
        language-specific shard
             ↓
        selected passages
             ↓
        sentence chunks
             ↓
        exact-text deduplication
             ↓
        batch embeddings
             ↓
        Qdrant
    """

    SUPPORTED_LANGUAGES = {
        "eng_Latn",
        "hin_Deva",
        "ben_Beng",
        "guj_Gujr",
    }

    # English comes from the Hindi shard.
    # Hindi comes from Hindi shard.
    # Bengali comes from Bengali shard.
    # Gujarati comes from Gujarati shard.

    LANGUAGE_OFFSETS = {
        "eng_Latn": 100_000_000,
        "hin_Deva": 200_000_000,
        "ben_Beng": 300_000_000,
        "guj_Gujr": 400_000_000,
    }

    def __init__(
        self,
        split: str = "validation",
        max_records: int = 100,
        max_chars: int = 500,
    ) -> None:

        self.loader = MSMARCOXILoader(
            split=split
        )

        self.embedder = Embedder()

        self.store = QdrantStore(
            collection_name="brahma_msmarco",
            vector_size=384,
        )

        # max_records means PER LANGUAGE SHARD.
        #
        # With 100:
        #
        # Hindi    = 100
        # Bengali  = 100
        # Gujarati = 100
        #
        # English is additionally extracted from
        # the 100 Hindi rows.
        self.max_records = max_records

        self.max_chars = max_chars

    # =========================================================
    # RUN
    # =========================================================

    def run(
        self,
    ) -> dict[str, Any]:

        processed_by_language = {
            "hin_Deva": 0,
            "ben_Beng": 0,
            "guj_Gujr": 0,
        }

        skipped_by_language = {
            "hin_Deva": 0,
            "ben_Beng": 0,
            "guj_Gujr": 0,
        }

        total_passages = 0
        total_chunks = 0
        duplicate_chunks = 0

        vectors: list[list[float]] = []
        payloads: list[dict[str, Any]] = []
        ids: list[str] = []

        # -----------------------------------------------------
        # GLOBAL EXACT CHUNK DEDUPLICATION
        # -----------------------------------------------------

        seen_chunks: set[
            tuple[str, str]
        ] = set()

        # -----------------------------------------------------
        # RESET COLLECTION
        # -----------------------------------------------------

        self.store.recreate_collection()

        # -----------------------------------------------------
        # STREAM DATA
        # -----------------------------------------------------

        for row in self.loader.stream(
            max_records_per_language=self.max_records
        ):

            shard_lang = str(
                row.get(
                    "_msmarco_shard_lang",
                    "",
                )
            ).strip()

            if shard_lang not in (
                "hin_Deva",
                "ben_Beng",
                "guj_Gujr",
            ):
                continue

            processed_by_language[
                shard_lang
            ] += 1

            # -------------------------------------------------
            # CONTENT LANGUAGES FOR THIS SHARD
            # -------------------------------------------------

            if shard_lang == "hin_Deva":

                # Hindi shard provides:
                #
                # 1. English source passages
                # 2. Hindi translated passages

                languages_to_index = (
                    "eng_Latn",
                    "hin_Deva",
                )

            elif shard_lang == "ben_Beng":

                languages_to_index = (
                    "ben_Beng",
                )

            else:

                languages_to_index = (
                    "guj_Gujr",
                )

            # -------------------------------------------------
            # PROCESS EACH CONTENT LANGUAGE
            # -------------------------------------------------

            for content_lang in languages_to_index:

                if content_lang not in (
                    self.SUPPORTED_LANGUAGES
                ):
                    continue

                passages = (
                    self.loader.extract_passages(
                        row=row,
                        content_lang=content_lang,
                        selected_only=True,
                    )
                )

                total_passages += len(
                    passages
                )

                row_chunks: list[str] = []
                row_payloads: list[
                    dict[str, Any]
                ] = []
                row_ids: list[str] = []

                # -------------------------------------------------
                # PASSAGES → CHUNKS
                # -------------------------------------------------

                for passage in passages:

                    text = str(
                        passage.get(
                            "text",
                            "",
                        )
                    ).strip()

                    if not text:
                        continue

                    chunks = sentence_chunks(
                        text,
                        max_chars=self.max_chars,
                    )

                    for chunk_index, chunk in enumerate(
                        chunks
                    ):

                        chunk = chunk.strip()

                        if not chunk:
                            continue

                        # -----------------------------------------
                        # EXACT CONTENT-LANGUAGE DEDUPLICATION
                        # -----------------------------------------

                        dedupe_key = (
                            content_lang,
                            chunk,
                        )

                        if dedupe_key in seen_chunks:

                            duplicate_chunks += 1

                            continue

                        seen_chunks.add(
                            dedupe_key
                        )

                        # -----------------------------------------
                        # PAYLOAD
                        # -----------------------------------------

                        payload = {
                            "query_id": str(
                                row.get(
                                    "query_id",
                                    "",
                                )
                            ),

                            "query_type": row.get(
                                "query_type",
                                "",
                            ),

                            "source_lang": row.get(
                                "source_lang",
                                "eng_Latn",
                            ),

                            "target_lang": row.get(
                                "target_lang",
                                "",
                            ),

                            "content_lang": (
                                content_lang
                            ),

                            "query": row.get(
                                "query",
                                "",
                            ),

                            "english_query": row.get(
                                "Eng_Query",
                                "",
                            ),

                            "answer": row.get(
                                "Answer",
                                "",
                            ),

                            "english_answer": row.get(
                                "Eng_Answer",
                                "",
                            ),

                            "passage_index": int(
                                passage.get(
                                    "passage_index",
                                    0,
                                )
                            ),

                            "is_selected": bool(
                                passage.get(
                                    "is_selected",
                                    True,
                                )
                            ),

                            "chunk_index": (
                                chunk_index
                            ),

                            "chunk_strategy": (
                                "sentence"
                            ),

                            "text": chunk,
                        }

                        # -----------------------------------------
                        # UNIQUE INTEGER ID
                        # -----------------------------------------

                        shard_record_index = int(
                            row.get(
                                "_msmarco_shard_record_index",
                                processed_by_language[
                                    shard_lang
                                ],
                            )
                        )

                        point_id = (
                            self._language_offset(
                                content_lang
                            )
                            + (
                                shard_record_index
                                * 1_000_000
                            )
                            + (
                                int(
                                    passage.get(
                                        "passage_index",
                                        0,
                                    )
                                )
                                * 1_000
                            )
                            + chunk_index
                        )

                        row_chunks.append(
                            chunk
                        )

                        row_payloads.append(
                            payload
                        )

                        row_ids.append(
                            str(point_id)
                        )

                        total_chunks += 1

                # -------------------------------------------------
                # BATCH EMBEDDING
                # -------------------------------------------------

                if row_chunks:

                    row_vectors = (
                        self.embedder.embed_texts(
                            row_chunks
                        )
                    )

                    vectors.extend(
                        row_vectors
                    )

                    payloads.extend(
                        row_payloads
                    )

                    ids.extend(
                        row_ids
                    )

            # -------------------------------------------------
            # PROGRESS
            # -------------------------------------------------

            print(
                f"Hindi: "
                f"{processed_by_language['hin_Deva']} | "
                f"Bengali: "
                f"{processed_by_language['ben_Beng']} | "
                f"Gujarati: "
                f"{processed_by_language['guj_Gujr']} | "
                f"Passages: "
                f"{total_passages} | "
                f"Chunks: "
                f"{total_chunks} | "
                f"Duplicates: "
                f"{duplicate_chunks}"
            )

        # -----------------------------------------------------
        # UPSERT
        # -----------------------------------------------------

        if vectors:

            self.store.upsert(
                vectors=vectors,
                payloads=payloads,
                ids=ids,
            )

        self.store.close()

        # -----------------------------------------------------
        # STATS
        # -----------------------------------------------------

        total_records = sum(
            processed_by_language.values()
        )

        total_skipped = sum(
            skipped_by_language.values()
        )

        return {
            "records": total_records,
            "skipped": total_skipped,
            "skipped_records": total_skipped,

            "records_hindi": (
                processed_by_language[
                    "hin_Deva"
                ]
            ),

            "records_bengali": (
                processed_by_language[
                    "ben_Beng"
                ]
            ),

            "records_gujarati": (
                processed_by_language[
                    "guj_Gujr"
                ]
            ),

            "passages": total_passages,
            "chunks": total_chunks,
            "vectors": len(vectors),
            "duplicate_chunks": duplicate_chunks,
        }

    # =========================================================
    # LANGUAGE OFFSET
    # =========================================================

    @classmethod
    def _language_offset(
        cls,
        language: str,
    ) -> int:

        try:
            return cls.LANGUAGE_OFFSETS[
                language
            ]

        except KeyError as exc:

            raise ValueError(
                f"Unsupported content language: "
                f"{language}"
            ) from exc
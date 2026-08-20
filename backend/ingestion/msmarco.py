from collections.abc import Iterator
from typing import Any

from datasets import Dataset
from huggingface_hub import hf_hub_download


class MSMARCOXILoader:
    """
    MSMARCO-XI loader for BRAHMA.

    User-facing languages:
        English
        Hindi
        Bengali
        Gujarati
        Hinglish

    Indexed dataset content:
        eng_Latn
        hin_Deva
        ben_Beng
        guj_Gujr

    Hinglish is NOT stored as a separate language.
    Hinglish queries retrieve from English + Hindi.

    Dataset shards:
        validation/hinval.parquet
        validation/benval.parquet
        validation/gujval.parquet

    English content is taken from the Hindi shard because
    MSMARCO-XI does not provide a separate English validation
    shard in this dataset repository.
    """

    REPO_ID = "ai4bharat/MSMARCO-XI"

    SHARDS = {
        "hin_Deva": "validation/hinval.parquet",
        "ben_Beng": "validation/benval.parquet",
        "guj_Gujr": "validation/gujval.parquet",
    }

    SUPPORTED_CONTENT_LANGUAGES = {
        "eng_Latn",
        "hin_Deva",
        "ben_Beng",
        "guj_Gujr",
    }

    SHARD_ORDER = (
        "hin_Deva",
        "ben_Beng",
        "guj_Gujr",
    )

    def __init__(
        self,
        split: str = "validation",
    ) -> None:

        if split != "validation":
            raise ValueError(
                "BRAHMA currently supports only "
                "the validation split."
            )

        self.split = split

    # =========================================================
    # DOWNLOAD
    # =========================================================

    def _download_shard(
        self,
        shard_lang: str,
    ) -> str:

        if shard_lang not in self.SHARDS:
            raise ValueError(
                f"Unsupported shard language: {shard_lang}"
            )

        return hf_hub_download(
            repo_id=self.REPO_ID,
            filename=self.SHARDS[shard_lang],
            repo_type="dataset",
        )

    # =========================================================
    # STREAM
    # =========================================================

    def stream(
        self,
        max_records_per_language: int | None = None,
    ) -> Iterator[dict[str, Any]]:
        """
        Stream rows from every required language shard.

        IMPORTANT:
        The record limit is applied PER LANGUAGE SHARD,
        not globally.

        Example:
            max_records_per_language=100

        gives approximately:

            Hindi    -> 100 rows
            Bengali  -> 100 rows
            Gujarati -> 100 rows

        English is derived from the Hindi shard.
        """

        for shard_lang in self.SHARD_ORDER:

            local_file = self._download_shard(
                shard_lang
            )

            dataset = Dataset.from_parquet(
                local_file
            )

            shard_count = 0

            for row in dataset:

                if (
                    max_records_per_language is not None
                    and shard_count >= max_records_per_language
                ):
                    break

                row = dict(row)

                row["_msmarco_shard_lang"] = (
                    shard_lang
                )

                row["_msmarco_shard_record_index"] = (
                    shard_count
                )

                shard_count += 1

                yield row

    # =========================================================
    # PASSAGE EXTRACTION
    # =========================================================

    @staticmethod
    def extract_passages(
        row: dict[str, Any],
        content_lang: str,
        selected_only: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Extract passages belonging to exactly one
        requested content language.

        English:
            passages["English_passages"]

        Hindi/Bengali/Gujarati:
            passages["Translated_passages"]
        """

        if content_lang not in (
            "eng_Latn",
            "hin_Deva",
            "ben_Beng",
            "guj_Gujr",
        ):
            return []

        passages = row.get(
            "passages",
            {},
        )

        if not isinstance(
            passages,
            dict,
        ):
            return []

        # -----------------------------------------------------
        # ENGLISH
        # -----------------------------------------------------

        if content_lang == "eng_Latn":

            texts = passages.get(
                "English_passages",
                [],
            )

        # -----------------------------------------------------
        # TRANSLATED LANGUAGE
        # -----------------------------------------------------

        else:

            texts = passages.get(
                "Translated_passages",
                [],
            )

        selected = passages.get(
            "is_selected",
            [],
        )

        if not isinstance(
            texts,
            list,
        ):
            return []

        if not isinstance(
            selected,
            list,
        ):
            selected = [
                1
                for _ in texts
            ]

        results: list[
            dict[str, Any]
        ] = []

        for index, text in enumerate(
            texts
        ):

            if not isinstance(
                text,
                str,
            ):
                continue

            text = text.strip()

            if not text:
                continue

            is_selected = (
                bool(selected[index])
                if index < len(selected)
                else False
            )

            if (
                selected_only
                and not is_selected
            ):
                continue

            results.append(
                {
                    "text": text,
                    "passage_index": index,
                    "is_selected": is_selected,
                    "content_lang": content_lang,
                }
            )

        return results

    # =========================================================
    # DOCUMENT
    # =========================================================

    @staticmethod
    def to_document(
        row: dict[str, Any],
    ) -> dict[str, Any]:

        return {
            "query_id": row.get(
                "query_id",
                "",
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

            "passages": row.get(
                "passages",
                {},
            ),

            "_msmarco_shard_lang": row.get(
                "_msmarco_shard_lang",
                "",
            ),
        }
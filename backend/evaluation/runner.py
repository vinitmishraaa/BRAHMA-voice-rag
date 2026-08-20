import json
import re
from collections import defaultdict
from pathlib import Path
from statistics import mean, median

from embeddings.embedder import Embedder
from retrieval.qdrant import QdrantStore


ROOT = Path(__file__).resolve().parent.parent
RESULT_DIR = ROOT / "evaluation" / "results"

COLLECTION = "brahma_msmarco"
VECTOR_SIZE = 384
MIN_SCORE = 0.60
TOP_K = 10

LANGUAGES = {
    "english": ["eng_Latn"],
    "hindi": ["hin_Deva"],
    "bengali": ["ben_Beng"],
    "gujarati": ["guj_Gujr"],
    "hinglish": ["eng_Latn", "hin_Deva"],
}


def mean_or_zero(values):
    return mean(values) if values else 0.0


def percentile(values, p):
    if not values:
        return 0.0

    values = sorted(values)

    if len(values) == 1:
        return float(values[0])

    position = (len(values) - 1) * p
    lower = int(position)
    upper = min(lower + 1, len(values))

    if lower == upper:
        return float(values[lower])

    weight = position - lower

    return (
        values[lower] * (1 - weight)
        + values[upper] * weight
    )


def hinglishify(text):
    """
    Lightweight deterministic Hinglish query conversion.

    This is intentionally conservative. It changes only
    common question forms and leaves entity/topic words intact.
    """

    text = text.strip()

    patterns = [
        (
            r"^what is (.+?)\??$",
            lambda m: f"{m.group(1)} kya hai?",
        ),
        (
            r"^what are (.+?)\??$",
            lambda m: f"{m.group(1)} kya hain?",
        ),
        (
            r"^who is (.+?)\??$",
            lambda m: f"{m.group(1)} kaun hai?",
        ),
        (
            r"^where is (.+?)\??$",
            lambda m: f"{m.group(1)} kahan hai?",
        ),
        (
            r"^when is (.+?)\??$",
            lambda m: f"{m.group(1)} kab hai?",
        ),
    ]

    lower = text.lower()

    for pattern, builder in patterns:
        match = re.match(pattern, lower)

        if match:
            return builder(match)

    return f"{text} kya hota hai?"


def collect_gold_queries(store, per_language=20):
    """
    Build evaluation cases directly from the indexed dataset payload.

    This guarantees that every evaluation query corresponds to an
    actual indexed query_id.
    """

    buckets = defaultdict(dict)

    offset = None

    while True:

        points, offset = store.client.scroll(
            collection_name=COLLECTION,
            limit=256,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )

        for point in points:

            payload = point.payload or {}

            query_id = str(
                payload.get("query_id", "")
            ).strip()

            content_lang = str(
                payload.get("content_lang", "")
            ).strip()

            query = str(
                payload.get("query", "")
            ).strip()

            english_query = str(
                payload.get("english_query", "")
            ).strip()

            if not query_id:
                continue

            if not query and not english_query:
                continue

            # Use one representative payload per query.
            key = (query_id, content_lang)

            if key not in buckets:
                buckets[key] = payload

        if offset is None:
            break

    cases = []

    # ---------------------------------------------------------
    # ENGLISH
    # ---------------------------------------------------------

    english_items = []

    for (query_id, lang), payload in buckets.items():

        if lang != "eng_Latn":
            continue

        query = (
            payload.get("english_query")
            or payload.get("query")
            or ""
        ).strip()

        if not query:
            continue

        english_items.append(
            {
                "id": f"eng_{query_id}",
                "language": "english",
                "query": query,
                "expected_query_id": query_id,
                "expected_content_language": "eng_Latn",
            }
        )

    # ---------------------------------------------------------
    # HINDI
    # ---------------------------------------------------------

    hindi_items = []

    for (query_id, lang), payload in buckets.items():

        if lang != "hin_Deva":
            continue

        query = str(
            payload.get("query", "")
        ).strip()

        if not query:
            continue

        hindi_items.append(
            {
                "id": f"hin_{query_id}",
                "language": "hindi",
                "query": query,
                "expected_query_id": query_id,
                "expected_content_language": "hin_Deva",
            }
        )

    # ---------------------------------------------------------
    # BENGALI
    # ---------------------------------------------------------

    bengali_items = []

    for (query_id, lang), payload in buckets.items():

        if lang != "ben_Beng":
            continue

        query = str(
            payload.get("query", "")
        ).strip()

        if not query:
            continue

        bengali_items.append(
            {
                "id": f"ben_{query_id}",
                "language": "bengali",
                "query": query,
                "expected_query_id": query_id,
                "expected_content_language": "ben_Beng",
            }
        )

    # ---------------------------------------------------------
    # GUJARATI
    # ---------------------------------------------------------

    gujarati_items = []

    for (query_id, lang), payload in buckets.items():

        if lang != "guj_Gujr":
            continue

        query = str(
            payload.get("query", "")
        ).strip()

        if not query:
            continue

        gujarati_items.append(
            {
                "id": f"guj_{query_id}",
                "language": "gujarati",
                "query": query,
                "expected_query_id": query_id,
                "expected_content_language": "guj_Gujr",
            }
        )

    # Sort deterministically.
    english_items.sort(key=lambda x: x["expected_query_id"])
    hindi_items.sort(key=lambda x: x["expected_query_id"])
    bengali_items.sort(key=lambda x: x["expected_query_id"])
    gujarati_items.sort(key=lambda x: x["expected_query_id"])

    english_items = english_items[:per_language]
    hindi_items = hindi_items[:per_language]
    bengali_items = bengali_items[:per_language]
    gujarati_items = gujarati_items[:per_language]

    cases.extend(english_items)
    cases.extend(hindi_items)
    cases.extend(bengali_items)
    cases.extend(gujarati_items)

    # ---------------------------------------------------------
    # HINGLISH
    # ---------------------------------------------------------

    hinglish_items = []

    for item in english_items:

        hinglish_query = hinglishify(
            item["query"]
        )

        hinglish_items.append(
            {
                "id": (
                    "hinglish_"
                    + item["expected_query_id"]
                ),
                "language": "hinglish",
                "query": hinglish_query,
                "expected_query_id": (
                    item["expected_query_id"]
                ),
                "expected_content_language": (
                    "eng_Latn"
                ),
            }
        )

    cases.extend(hinglish_items)

    return cases


def evaluate_case(
    embedder,
    store,
    item,
):
    import time

    start = time.perf_counter()

    vector = embedder.embed_query(
        item["query"]
    )

    embedding_ms = (
        time.perf_counter() - start
    ) * 1000

    start = time.perf_counter()

    results = store.search(
        query_vector=vector,
        limit=TOP_K,
        content_languages=LANGUAGES[
            item["language"]
        ],
    )

    retrieval_ms = (
        time.perf_counter() - start
    ) * 1000

    expected_id = str(
        item["expected_query_id"]
    )

    rank = None
    score = None
    language_ok = False

    seen = set()

    for index, result in enumerate(
        results,
        start=1,
    ):

        payload = result.payload or {}

        query_id = str(
            payload.get("query_id", "")
        )

        content_lang = str(
            payload.get("content_lang", "")
        )

        text = str(
            payload.get("text", "")
        ).strip()

        # Duplicate-content diagnostic.
        seen.add(
            (
                content_lang,
                text,
            )
        )

        if (
            query_id == expected_id
            and rank is None
        ):
            rank = index
            score = float(result.score)

            if item["language"] == "hinglish":
                language_ok = content_lang in (
                    "eng_Latn",
                    "hin_Deva",
                )
            else:
                language_ok = (
                    content_lang
                    == item[
                        "expected_content_language"
                    ]
                )

    return {
        "id": item["id"],
        "language": item["language"],
        "query": item["query"],
        "expected_query_id": expected_id,
        "rank": rank,
        "score": score,
        "retrieved": rank is not None,
        "language_ok": language_ok,
        "recall_1": (
            1.0
            if rank is not None
            and rank <= 1
            else 0.0
        ),
        "recall_5": (
            1.0
            if rank is not None
            and rank <= 5
            else 0.0
        ),
        "recall_10": (
            1.0
            if rank is not None
            and rank <= 10
            else 0.0
        ),
        "rr10": (
            1.0 / rank
            if rank is not None
            else 0.0
        ),
        "embedding_ms": embedding_ms,
        "retrieval_ms": retrieval_ms,
        "total_ms": (
            embedding_ms
            + retrieval_ms
        ),
    }


def print_language_summary(
    language,
    rows,
):
    print(f"\n{language.upper()}")
    print("-" * 70)

    print(
        f"Queries       : {len(rows)}"
    )

    print(
        f"Recall@1      : "
        f"{mean_or_zero([r['recall_1'] for r in rows]):.4f}"
    )

    print(
        f"Recall@5      : "
        f"{mean_or_zero([r['recall_5'] for r in rows]):.4f}"
    )

    print(
        f"Recall@10     : "
        f"{mean_or_zero([r['recall_10'] for r in rows]):.4f}"
    )

    print(
        f"MRR@10        : "
        f"{mean_or_zero([r['rr10'] for r in rows]):.4f}"
    )

    print(
        f"Language Acc. : "
        f"{mean_or_zero([1.0 if r['language_ok'] else 0.0 for r in rows]):.4f}"
    )

    print(
        f"Avg Total ms  : "
        f"{mean_or_zero([r['total_ms'] for r in rows]):.2f}"
    )

    print(
        f"P50 Total ms  : "
        f"{percentile([r['total_ms'] for r in rows], 0.50):.2f}"
    )

    print(
        f"P95 Total ms  : "
        f"{percentile([r['total_ms'] for r in rows], 0.95):.2f}"
    )


def main():

    print("=" * 70)
    print("BRAHMA MULTILINGUAL RETRIEVAL EVALUATION")
    print("=" * 70)

    print(
        "\nEvaluation design:"
    )

    print(
        "20 queries per language + 20 Hinglish queries"
    )

    print(
        "Ground truth: indexed MSMARCO-XI query_id"
    )

    print(
        "Metrics: Recall@1, Recall@5, Recall@10, MRR@10"
    )

    embedder = Embedder()

    store = QdrantStore(
        collection_name=COLLECTION,
        vector_size=VECTOR_SIZE,
        min_score=MIN_SCORE,
    )

    try:

        cases = collect_gold_queries(
            store,
            per_language=20,
        )

        if not cases:
            raise RuntimeError(
                "No evaluation queries found in Qdrant."
            )

        print(
            f"\nEvaluation cases generated: "
            f"{len(cases)}"
        )

        by_language = defaultdict(list)

        for item in cases:
            by_language[
                item["language"]
            ].append(item)

        print("\nCases by language:")

        for language in (
            "english",
            "hindi",
            "bengali",
            "gujarati",
            "hinglish",
        ):

            print(
                f"  {language:<10}: "
                f"{len(by_language[language])}"
            )

        all_results = []

        print(
            "\nRunning evaluation..."
        )

        for index, item in enumerate(
            cases,
            start=1,
        ):

            result = evaluate_case(
                embedder,
                store,
                item,
            )

            all_results.append(result)

            status = (
                "PASS"
                if result["retrieved"]
                else "MISS"
            )

            rank_text = (
                str(result["rank"])
                if result["rank"]
                else "-"
            )

            score_text = (
                f"{result['score']:.4f}"
                if result["score"] is not None
                else "-"
            )

            print(
                f"[{index:03d}/{len(cases):03d}] "
                f"{item['language']:<10} "
                f"RANK={rank_text:<3} "
                f"SCORE={score_text:<7} "
                f"{status} "
                f"{item['query'][:55]}"
            )

        # -----------------------------------------------------
        # SUMMARIES
        # -----------------------------------------------------

        print("\n")
        print("=" * 70)
        print("RESULTS BY LANGUAGE")
        print("=" * 70)

        for language in (
            "english",
            "hindi",
            "bengali",
            "gujarati",
            "hinglish",
        ):

            print_language_summary(
                language,
                by_language_results(
                    all_results,
                    language,
                ),
            )

        # -----------------------------------------------------
        # OVERALL
        # -----------------------------------------------------

        print("\n")
        print("=" * 70)
        print("OVERALL RESULTS")
        print("=" * 70)

        print(
            f"Total Queries  : "
            f"{len(all_results)}"
        )

        print(
            f"Recall@1       : "
            f"{mean_or_zero([r['recall_1'] for r in all_results]):.4f}"
        )

        print(
            f"Recall@5       : "
            f"{mean_or_zero([r['recall_5'] for r in all_results]):.4f}"
        )

        print(
            f"Recall@10      : "
            f"{mean_or_zero([r['recall_10'] for r in all_results]):.4f}"
        )

        print(
            f"MRR@10         : "
            f"{mean_or_zero([r['rr10'] for r in all_results]):.4f}"
        )

        print(
            f"Language Acc.  : "
            f"{mean_or_zero([1.0 if r['language_ok'] else 0.0 for r in all_results]):.4f}"
        )

        latencies = [
            r["total_ms"]
            for r in all_results
        ]

        print(
            f"Avg Latency    : "
            f"{mean_or_zero(latencies):.2f} ms"
        )

        print(
            f"Median Latency : "
            f"{median(latencies):.2f} ms"
        )

        print(
            f"P95 Latency    : "
            f"{percentile(latencies, 0.95):.2f} ms"
        )

        print(
            f"Successful     : "
            f"{sum(r['retrieved'] for r in all_results)}"
            f"/{len(all_results)}"
        )

        # -----------------------------------------------------
        # SAVE RESULTS
        # -----------------------------------------------------

        RESULT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_file = (
            RESULT_DIR
            / "retrieval_results.json"
        )

        with open(
            output_file,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                all_results,
                file,
                ensure_ascii=False,
                indent=2,
            )

        print(
            "\nSaved:"
        )

        print(
            output_file
        )

        print("=" * 70)

    finally:

        store.close()


def by_language_results(
    results,
    language,
):
    return [
        result
        for result in results
        if result["language"] == language
    ]


if __name__ == "__main__":
    main()
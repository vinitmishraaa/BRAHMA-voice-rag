from embeddings.embedder import Embedder
from retrieval.qdrant import QdrantStore


# ============================================================
# CONFIG
# ============================================================

ALLOWED_CONTENT_LANGUAGES = {
    "eng_Latn",
    "hin_Deva",
    "ben_Beng",
    "guj_Gujr",
}

MIN_SCORE = 0.70
TOP_K = 5


# ============================================================
# MODELS
# ============================================================

embedder = Embedder()

store = QdrantStore(
    collection_name="brahma_msmarco",
    vector_size=384,
    min_score=MIN_SCORE,
)


# ============================================================
# TEST
# ============================================================

def run_query(
    name: str,
    query: str,
    languages: list[str],
) -> bool:

    print("\n" + "=" * 70)
    print(name)
    print("=" * 70)

    print("Query:", query)
    print("Retrieval languages:", languages)
    print("Minimum score:", MIN_SCORE)

    query_vector = embedder.embed_query(
        query
    )

    results = store.search(
        query_vector=query_vector,
        limit=TOP_K,
        content_languages=languages,
        min_score=MIN_SCORE,
    )

    if not results:

        print("\nNO RESULTS")
        return False

    valid = True

    seen_content: set[
        tuple[str, str]
    ] = set()

    seen_query_ids: set[
        str
    ] = set()

    for index, result in enumerate(
        results,
        start=1,
    ):

        payload = result.payload or {}

        score = float(result.score)

        content_lang = payload.get(
            "content_lang"
        )

        query_id = str(
            payload.get(
                "query_id",
                "",
            )
        )

        text = str(
            payload.get(
                "text",
                "",
            )
        ).strip()

        print(
            f"\n--- Result {index} ---"
        )

        print(
            "Score:",
            round(score, 4),
        )

        print(
            "Content language:",
            content_lang,
        )

        print(
            "Query ID:",
            query_id,
        )

        print(
            "Text:",
            text,
        )

        # ----------------------------------------------------
        # SCORE CHECK
        # ----------------------------------------------------

        if score < MIN_SCORE:

            print(
                "FAIL: score below threshold"
            )

            valid = False

        # ----------------------------------------------------
        # LANGUAGE CHECK
        # ----------------------------------------------------

        if content_lang not in (
            ALLOWED_CONTENT_LANGUAGES
        ):

            print(
                "FAIL: unsupported content language"
            )

            valid = False

        # ----------------------------------------------------
        # REQUESTED LANGUAGE CHECK
        # ----------------------------------------------------

        if content_lang not in languages:

            print(
                "FAIL: result language "
                "was not requested"
            )

            valid = False

        # ----------------------------------------------------
        # EMPTY CONTENT CHECK
        # ----------------------------------------------------

        if not text:

            print(
                "FAIL: empty content"
            )

            valid = False

        # ----------------------------------------------------
        # DUPLICATE CONTENT CHECK
        # ----------------------------------------------------

        content_key = (
            str(content_lang),
            text,
        )

        if content_key in seen_content:

            print(
                "FAIL: duplicate content"
            )

            valid = False

        seen_content.add(
            content_key
        )

        # ----------------------------------------------------
        # QUERY ID INFORMATION
        # ----------------------------------------------------

        if query_id in seen_query_ids:

            print(
                "INFO: same query_id appears "
                "more than once"
            )

        seen_query_ids.add(
            query_id
        )

    # --------------------------------------------------------
    # FINAL TEST RESULT
    # --------------------------------------------------------

    if valid:

        print("\nPASS")

    else:

        print("\nFAIL")

    return valid


# ============================================================
# TEST CASES
# ============================================================

tests = [

    (
        "ENGLISH TEST",
        "what is a corporation?",
        ["eng_Latn"],
    ),

    (
        "HINDI TEST",
        "कॉरपोरेशन क्या है?",
        ["hin_Deva"],
    ),

    (
        "BENGALI TEST",
        "কর্পোরেশন কী?",
        ["ben_Beng"],
    ),

    (
        "GUJARATI TEST",
        "કોર્પોરેશન શું છે?",
        ["guj_Gujr"],
    ),

    (
        "HINGLISH TEST",
        "corporation kya hota hai?",
        [
            "eng_Latn",
            "hin_Deva",
        ],
    ),
]


# ============================================================
# RUN
# ============================================================

all_passed = True

for name, query, languages in tests:

    passed = run_query(
        name=name,
        query=query,
        languages=languages,
    )

    if not passed:
        all_passed = False


store.close()


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 70)

if all_passed:

    print(
        "RETRIEVAL TEST PASSED"
    )

else:

    print(
        "RETRIEVAL TEST FAILED"
    )

print("=" * 70)

print(
    "Allowed indexed languages:",
    sorted(
        ALLOWED_CONTENT_LANGUAGES
    ),
)

print(
    "Minimum similarity score:",
    MIN_SCORE,
)

print("=" * 70)


if not all_passed:
    raise SystemExit(1)
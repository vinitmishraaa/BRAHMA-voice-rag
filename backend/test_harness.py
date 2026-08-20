import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BASE_URL = (
    "http://127.0.0.1:8000"
)

QUERY_URL = (
    f"{BASE_URL}/api/v1/query"
)


TEST_QUERIES = [
    (
        "ENGLISH",
        "What is a corporation?",
    ),
    (
        "HINDI",
        "कॉरपोरेशन क्या है?",
    ),
    (
        "BENGALI",
        "কর্পোরেশন কী?",
    ),
    (
        "GUJARATI",
        "કોર્પોરેશન શું છે?",
    ),
    (
        "HINGLISH",
        "corporation kya hota hai?",
    ),
]


def call_api(
    query: str,
) -> dict:

    body = json.dumps(
        {
            "query": query,
        },
        ensure_ascii=False,
    ).encode("utf-8")

    request = Request(
        QUERY_URL,
        data=body,
        headers={
            "Content-Type": (
                "application/json"
            ),
        },
        method="POST",
    )

    with urlopen(
        request,
        timeout=30,
    ) as response:

        raw = response.read()

    return json.loads(
        raw.decode("utf-8")
    )


def run_test(
    label: str,
    query: str,
) -> bool:

    print()
    print("=" * 70)
    print(label)
    print("=" * 70)
    print("Query:", query)

    try:

        result = call_api(
            query
        )

        print(
            "HTTP/API Success:",
            result.get("success"),
        )

        print(
            "Language:",
            result.get("language"),
        )

        print(
            "Retrieval languages:",
            result.get(
                "retrieval_languages"
            ),
        )

        print(
            "Answer:",
            result.get("answer"),
        )

        latency = result.get(
            "latency",
            {},
        )

        print(
            "Latency:",
            f"{latency.get('total_ms', 0.0):.2f} ms",
        )

        confidence = result.get(
            "retrieval_confidence",
            {},
        )

        print(
            "Top score:",
            confidence.get(
                "top_score"
            ),
        )

        print(
            "Relevant context:",
            confidence.get(
                "has_relevant_context"
            ),
        )

        if not result.get(
            "success",
            False,
        ):
            print("FAIL")
            return False

        if not result.get(
            "answer"
        ):
            print("FAIL: empty answer")
            return False

        if not confidence.get(
            "has_relevant_context",
            False,
        ):
            print(
                "FAIL: no relevant context"
            )
            return False

        print("PASS")
        return True

    except HTTPError as exc:

        print(
            "HTTP ERROR:",
            exc.code,
        )

        try:
            print(
                exc.read().decode(
                    "utf-8"
                )
            )
        except Exception:
            pass

        return False

    except URLError as exc:

        print(
            "CONNECTION ERROR:",
            exc.reason,
        )

        print(
            "Make sure FastAPI is running."
        )

        return False

    except Exception as exc:

        print(
            "ERROR:",
            exc,
        )

        return False


def main() -> int:

    print("=" * 70)
    print("BRAHMA API BACKEND TEST")
    print("=" * 70)

    passed = 0
    total = len(
        TEST_QUERIES
    )

    for label, query in TEST_QUERIES:

        if run_test(
            label,
            query,
        ):
            passed += 1

    print()
    print("=" * 70)
    print("FINAL RESULT")
    print("=" * 70)

    print(
        f"Passed: {passed}/{total}"
    )

    if passed == total:
        print(
            "BACKEND API TEST PASSED"
        )
        return 0

    print(
        "BACKEND API TEST FAILED"
    )
    return 1


if __name__ == "__main__":
    sys.exit(
        main()
    )
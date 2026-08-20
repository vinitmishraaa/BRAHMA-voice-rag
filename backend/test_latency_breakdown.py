from harness.runner import BRAHMAHarness


QUERIES = [
    "What is a corporation?",
    "What is throughput?",
    "What is barter?",
    "What is a federal contractor?",
    "What is BASIC programming?",
    "कॉरपोरेशन क्या है?",
    "बार्टर क्या है?",
    "थ्रूपुट क्या है?",
    "फेडरल कॉन्ट्रैक्टर क्या है?",
    "BASIC प्रोग्रामिंग क्या है?",
    "corporation kya hota hai?",
    "barter kya hota hai?",
    "throughput kya hota hai?",
    "federal contractor kya hota hai?",
    "BASIC programming kya hai?",
]


def main() -> None:
    harness = BRAHMAHarness(
    )

    try:
        print("=" * 80)
        print("BRAHMA LATENCY BREAKDOWN")
        print("=" * 80)

        # Warm-up
        print("\nWarm-up...")

        for query in [
            "What is a corporation?",
            "कॉरपोरेशन क्या है?",
        ]:
            result = harness.run(query)

            print(
                f"{query} -> "
                f"{result.latency_ms:.2f} ms"
            )

        print("\nActual measurements:\n")

        for index, query in enumerate(
            QUERIES,
            start=1,
        ):
            result = harness.run(query)

            print(
                f"[{index:02d}] {query}"
            )

            if not result.success:
                print(
                    f"    ERROR: {result.error}"
                )
                continue

            stages = result.stages or {}

            print(
                f"    Language:    "
                f"{stages.get('language_ms', 0):.2f} ms"
            )

            print(
                f"    Embedding:   "
                f"{stages.get('embedding_ms', 0):.2f} ms"
            )

            print(
                f"    Retrieval:   "
                f"{stages.get('retrieval_ms', 0):.2f} ms"
            )

            print(
                f"    Context:     "
                f"{stages.get('context_ms', 0):.2f} ms"
            )

            print(
                f"    Generation:  "
                f"{stages.get('generation_ms', 0):.2f} ms"
            )

            print(
                f"    TOTAL:       "
                f"{stages.get('total_ms', 0):.2f} ms"
            )

            print()

    finally:
        harness.close()


if __name__ == "__main__":
    main()
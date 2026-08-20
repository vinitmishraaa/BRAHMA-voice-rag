import statistics
from time import perf_counter

from harness.runner import BRAHMAHarness


# ---------------------------------------------------------
# Benchmark configuration
# ---------------------------------------------------------

WARMUP_QUERIES = [
    "What is a corporation?",
    "कॉरपोरेशन क्या है?",
    "corporation kya hota hai?",
]

TEST_QUERIES = [
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


def percentile(
    values: list[float],
    percentage: float,
) -> float:
    """
    Calculate a percentile using linear interpolation.
    """

    if not values:
        return 0.0

    sorted_values = sorted(values)

    position = (
        (len(sorted_values) - 1)
        * (percentage / 100)
    )

    lower = int(position)
    upper = min(
        lower + 1,
        len(sorted_values) - 1,
    )

    fraction = position - lower

    return (
        sorted_values[lower]
        + (
            sorted_values[upper]
            - sorted_values[lower]
        )
        * fraction
    )


def run_query(
    harness: BRAHMAHarness,
    query: str,
) -> float:
    """
    Run one query and return end-to-end latency.
    """

    start = perf_counter()

    result = harness.run(query)

    # We intentionally measure the complete harness
    # execution independently from the latency reported
    # inside the harness.
    elapsed_ms = (
        perf_counter() - start
    ) * 1000

    if not result.success:
        print(
            f"FAILED | {query} | "
            f"{result.error}"
        )

    return elapsed_ms


def main() -> None:
    print("=" * 70)
    print("BRAHMA LATENCY BENCHMARK")
    print("=" * 70)

    harness = BRAHMAHarness(
        max_retries=1,
    )

    try:
        # -------------------------------------------------
        # Warm-up
        # -------------------------------------------------

        print("\nWarm-up phase...")

        for query in WARMUP_QUERIES:
            latency = run_query(
                harness,
                query,
            )

            print(
                f"Warm-up: "
                f"{latency:.2f} ms | "
                f"{query}"
            )

        # -------------------------------------------------
        # Actual benchmark
        # -------------------------------------------------

        print("\nBenchmark phase...")

        latencies = []

        for index, query in enumerate(
            TEST_QUERIES,
            start=1,
        ):
            latency = run_query(
                harness,
                query,
            )

            latencies.append(latency)

            print(
                f"[{index:02d}/{len(TEST_QUERIES)}] "
                f"{latency:.2f} ms | "
                f"{query}"
            )

        if not latencies:
            print(
                "\nNo latency measurements collected."
            )
            return

        # -------------------------------------------------
        # Statistics
        # -------------------------------------------------

        p50 = percentile(
            latencies,
            50,
        )

        p70 = percentile(
            latencies,
            70,
        )

        p100 = max(latencies)

        average = statistics.mean(
            latencies
        )

        minimum = min(latencies)

        maximum = max(latencies)

        under_200 = sum(
            1
            for latency in latencies
            if latency < 200
        )

        percentage_under_200 = (
            under_200
            / len(latencies)
            * 100
        )

        # -------------------------------------------------
        # Results
        # -------------------------------------------------

        print("\n")
        print("=" * 70)
        print("LATENCY RESULTS")
        print("=" * 70)

        print(
            f"Queries:              {len(latencies)}"
        )

        print(
            f"Minimum:              {minimum:.2f} ms"
        )

        print(
            f"Average:              {average:.2f} ms"
        )

        print(
            f"P50:                  {p50:.2f} ms"
        )

        print(
            f"P70:                  {p70:.2f} ms"
        )

        print(
            f"P100:                 {p100:.2f} ms"
        )

        print(
            f"Under 200 ms:         "
            f"{under_200}/{len(latencies)} "
            f"({percentage_under_200:.1f}%)"
        )

        print("=" * 70)

    finally:
        harness.close()


if __name__ == "__main__":
    main()
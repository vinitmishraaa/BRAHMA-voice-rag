from typing import Any


def recall_at_k(
    results: list[Any],
    expected_query_id: str,
    k: int,
) -> float:
    """
    Returns 1.0 if the expected query_id appears
    within the first k results, otherwise 0.0.
    """

    for result in results[:k]:
        payload = result.payload or {}

        query_id = str(
            payload.get("query_id", "")
        )

        if query_id == str(expected_query_id):
            return 1.0

    return 0.0


def reciprocal_rank(
    results: list[Any],
    expected_query_id: str,
    k: int = 10,
) -> float:

    for rank, result in enumerate(
        results[:k],
        start=1,
    ):
        payload = result.payload or {}

        query_id = str(
            payload.get("query_id", "")
        )

        if query_id == str(expected_query_id):
            return 1.0 / rank

    return 0.0


def mean(values: list[float]) -> float:
    if not values:
        return 0.0

    return sum(values) / len(values)
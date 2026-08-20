from rag.pipeline import RAGPipeline


pipeline = RAGPipeline(
    collection_name="brahma_msmarco",
    vector_size=1024,
    top_k=5,
)


def run_test(query: str) -> None:
    print("\n" + "=" * 70)
    print("QUERY:", query)
    print("=" * 70)

    result = pipeline.answer(query)

    print("Detected language:")
    print(result["language"])

    print("\nRetrieval languages:")
    print(result["retrieval_languages"])

    print("\nRetrieved context:")
    for index, context in enumerate(
        result["context"],
        start=1,
    ):
        print(f"\n--- Context {index} ---")
        print(context)

    print("\nFINAL ANSWER:")
    print(result["answer"])


try:
    run_test(
        "what is a corporation?"
    )

    run_test(
        "कॉरपोरेशन क्या है?"
    )

    run_test(
        "corporation kya hota hai?"
    )

finally:
    pipeline.close()
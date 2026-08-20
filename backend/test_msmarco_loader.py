from ingestion.msmarco import MSMARCOXILoader


loader = MSMARCOXILoader(split="validation")

row = next(loader.stream())

document = loader.to_document(row)

print("MSMARCO-XI loader OK")
print("Query ID:", document["query_id"])
print("Source:", document["source_lang"])
print("Target:", document["target_lang"])
print("Query:", document["query"])
print("Answer:", document["answer"])

passages = loader.extract_passages(
    row,
    use_translated=True,
    selected_only=True,
)

print("\nSelected translated passages:", len(passages))

for passage in passages:
    print(
        f"\nPassage {passage['passage_index']}:"
    )
    print(passage["text"])
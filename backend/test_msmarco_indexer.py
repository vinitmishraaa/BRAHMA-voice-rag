from ingestion.indexer import MSMARCOIndexer


indexer = MSMARCOIndexer(
    split="validation",
    max_records=100,
    max_chars=500,
)

stats = indexer.run()

print("\n" + "=" * 70)
print("MSMARCO-XI INDEXING COMPLETE")
print("=" * 70)

print("Records:", stats["records"])
print("Skipped:", stats["skipped_records"])
print("Passages:", stats["passages"])
print("Chunks:", stats["chunks"])
print("Vectors:", stats["vectors"])
print(
    "Duplicate chunks:",
    stats["duplicate_chunks"],
)

print("=" * 70)

print(
    "Expected indexed content languages:"
)

for language in [
    "eng_Latn",
    "hin_Deva",
    "ben_Beng",
    "guj_Gujr",
]:
    print(
        "  -",
        language,
    )

print("=" * 70)
from chunking.fixed import fixed_size_chunks
from chunking.metadata import create_chunk_metadata
from ingestion.cleaner import clean_text
from ingestion.loader import load_text
from ingestion.metadata import create_metadata


raw_text = load_text("test_document.txt")
cleaned_text = clean_text(raw_text)

document_metadata = create_metadata(
    "test_document.txt",
    cleaned_text,
)

chunks = fixed_size_chunks(
    cleaned_text,
    chunk_size=50,
    chunk_overlap=10,
)

chunk_metadata = create_chunk_metadata(
    document_metadata=document_metadata,
    chunks=chunks,
    chunking_method="fixed",
)

print(f"Total chunks: {len(chunk_metadata)}")

for item in chunk_metadata:
    print("\n--- Chunk Metadata ---")

    for key, value in item.items():
        print(f"{key}: {value}")
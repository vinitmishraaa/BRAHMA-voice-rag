from ingestion.loader import load_text
from ingestion.cleaner import clean_text
from chunking.fixed import fixed_size_chunks


raw_text = load_text("test_document.txt")
cleaned_text = clean_text(raw_text)

chunks = fixed_size_chunks(
    cleaned_text,
    chunk_size=50,
    chunk_overlap=10,
)

print(f"Total chunks: {len(chunks)}")

for index, chunk in enumerate(chunks, start=1):
    print(f"\n--- Chunk {index} ---")
    print(chunk)
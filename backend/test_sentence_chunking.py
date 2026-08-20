from ingestion.loader import load_text
from ingestion.cleaner import clean_text
from chunking.sentence import sentence_chunks


raw_text = load_text("test_document.txt")
cleaned_text = clean_text(raw_text)

chunks = sentence_chunks(
    cleaned_text,
    max_chars=80,
)

print(f"Total chunks: {len(chunks)}")

for index, chunk in enumerate(chunks, start=1):
    print(f"\n--- Chunk {index} ---")
    print(chunk)
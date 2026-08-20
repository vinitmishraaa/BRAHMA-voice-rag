from ingestion.loader import load_text
from ingestion.cleaner import clean_text
from ingestion.metadata import create_metadata

from chunking.sentence import sentence_chunks
from chunking.metadata import create_chunk_metadata

from embeddings.embedder import Embedder


# 1. Load
raw_text = load_text("test_document.txt")

# 2. Clean
cleaned_text = clean_text(raw_text)

# 3. Document metadata
document_metadata = create_metadata(
    "test_document.txt",
    cleaned_text,
)

# 4. Sentence chunking
chunks = sentence_chunks(
    cleaned_text,
    max_chars=200,
)

# 5. Chunk metadata
chunk_records = create_chunk_metadata(
    document_metadata=document_metadata,
    chunks=chunks,
    chunking_method="sentence",
)

# 6. Embeddings
embedder = Embedder()

texts = [record["text"] for record in chunk_records]
vectors = embedder.embed_texts(texts)

print("Pipeline successful")
print("Document:", document_metadata["file_name"])
print("Chunks:", len(chunk_records))
print("Vectors:", len(vectors))
print("Vector dimension:", len(vectors[0]))

for index, record in enumerate(chunk_records):
    print(
        f"Chunk {index}: "
        f"{record['character_count']} chars | "
        f"vector={len(vectors[index])} dims"
    )
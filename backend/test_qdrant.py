from ingestion.loader import load_text
from ingestion.cleaner import clean_text
from ingestion.metadata import create_metadata

from chunking.sentence import sentence_chunks
from chunking.metadata import create_chunk_metadata

from embeddings.embedder import Embedder
from retrieval.qdrant import QdrantStore


# Load + clean
raw_text = load_text("test_document.txt")
cleaned_text = clean_text(raw_text)

# Document metadata
document_metadata = create_metadata(
    "test_document.txt",
    cleaned_text,
)

# Chunk
chunks = sentence_chunks(
    cleaned_text,
    max_chars=200,
)

chunk_records = create_chunk_metadata(
    document_metadata=document_metadata,
    chunks=chunks,
    chunking_method="sentence",
)

# Embeddings
embedder = Embedder()

texts = [record["text"] for record in chunk_records]
vectors = embedder.embed_texts(texts)

# Qdrant
store = QdrantStore()

store.upsert(
    vectors=vectors,
    payloads=chunk_records,
)

print("Qdrant upsert successful")
print("Stored points:", len(vectors))

# Search
query = "What is BRAHMA?"
query_vector = embedder.embed_text(query)

results = store.search(
    query_vector=query_vector,
    limit=3,
)

print("\nSearch results:")

for result in results:
    print("\nScore:", result.score)
    print("Text:", result.payload["text"])

store.close()
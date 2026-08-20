import os

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import PayloadSchemaType

load_dotenv()

COLLECTION = "brahma_msmarco"

url = os.getenv("QDRANT_URL")
api_key = os.getenv("QDRANT_API_KEY")

if not url:
    raise RuntimeError("QDRANT_URL missing")

if not api_key:
    raise RuntimeError("QDRANT_API_KEY missing")

print("=" * 70)
print("BRAHMA QDRANT CLOUD INDEX FIX")
print("=" * 70)

client = QdrantClient(
    url=url,
    api_key=api_key,
    timeout=60,
)

print("\nCreating payload index...")
print("Collection:", COLLECTION)
print("Field: content_lang")
print("Type: keyword")

client.create_payload_index(
    collection_name=COLLECTION,
    field_name="content_lang",
    field_schema=PayloadSchemaType.KEYWORD,
    wait=True,
)

print("\nPayload index created successfully.")

collection_info = client.get_collection(
    COLLECTION
)

print(
    "Points:",
    collection_info.points_count,
)

print("\n" + "=" * 70)
print("QDRANT CLOUD READY")
print("=" * 70)

client.close()
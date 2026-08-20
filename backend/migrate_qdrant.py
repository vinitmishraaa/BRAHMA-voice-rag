import os
import time

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

load_dotenv()

COLLECTION = "brahma_msmarco"

LOCAL_PATH = "./qdrant_data"

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

if not QDRANT_URL:
    raise RuntimeError("QDRANT_URL is missing from .env")

if not QDRANT_API_KEY:
    raise RuntimeError("QDRANT_API_KEY is missing from .env")


print("=" * 70)
print("BRAHMA → QDRANT CLOUD MIGRATION")
print("=" * 70)

# ------------------------------------------------------------------
# CLIENTS
# ------------------------------------------------------------------

print("\nConnecting to local Qdrant...")

local = QdrantClient(
    path=LOCAL_PATH,
)

print("Connecting to Qdrant Cloud...")

cloud = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    timeout=300,
)

# ------------------------------------------------------------------
# LOCAL COLLECTION
# ------------------------------------------------------------------

print("\nChecking local collection...")

if not local.collection_exists(COLLECTION):
    raise RuntimeError(
        f"Local collection '{COLLECTION}' does not exist."
    )

local_info = local.get_collection(COLLECTION)

local_count = local.count(
    collection_name=COLLECTION,
    exact=True,
).count

print(f"Collection: {COLLECTION}")
print(f"Local points: {local_count}")

try:
    vector_size = local_info.config.params.vectors.size
    distance = local_info.config.params.vectors.distance

    print(f"Vector size: {vector_size}")
    print(f"Distance: {distance}")

except Exception:
    print("Could not read vector configuration.")

# ------------------------------------------------------------------
# CLOUD COLLECTION
# ------------------------------------------------------------------

print("\nChecking Cloud collection...")

if not cloud.collection_exists(COLLECTION):

    print("Cloud collection does not exist.")
    print("Creating Cloud collection...")

    cloud.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE,
        ),
    )

    print("Cloud collection created.")

else:
    print("Cloud collection already exists.")

# ------------------------------------------------------------------
# MIGRATION
# ------------------------------------------------------------------

print("\nMigrating points...")

BATCH_SIZE = 50
MAX_RETRIES = 5

offset = None
migrated = 0

while True:

    records, next_offset = local.scroll(
        collection_name=COLLECTION,
        limit=BATCH_SIZE,
        offset=offset,
        with_payload=True,
        with_vectors=True,
    )

    if not records:
        break

    cloud_points = []

    for record in records:

        cloud_points.append(
            PointStruct(
                id=record.id,
                vector=record.vector,
                payload=record.payload,
            )
        )

    # --------------------------------------------------------------
    # RETRY BATCH
    # --------------------------------------------------------------

    success = False

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            cloud.upsert(
                collection_name=COLLECTION,
                points=cloud_points,
                wait=True,
            )

            success = True
            break

        except Exception as exc:

            print(
                f"  Batch upload failed "
                f"(attempt {attempt}/{MAX_RETRIES}): {exc}"
            )

            if attempt < MAX_RETRIES:
                wait_time = attempt * 3

                print(
                    f"  Retrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)

    if not success:
        raise RuntimeError(
            "Migration stopped because a batch could not "
            "be uploaded after multiple retries."
        )

    migrated += len(cloud_points)

    print(
        f"  Migrated {migrated}/{local_count} points"
    )

    offset = next_offset

    if offset is None:
        break

# ------------------------------------------------------------------
# VERIFY
# ------------------------------------------------------------------

print("\nVerifying Cloud collection...")

cloud_count = cloud.count(
    collection_name=COLLECTION,
    exact=True,
).count

print(f"Local points : {local_count}")
print(f"Cloud points : {cloud_count}")

if cloud_count != local_count:

    raise RuntimeError(
        f"Migration verification failed: "
        f"local={local_count}, cloud={cloud_count}"
    )

print("\n" + "=" * 70)
print("MIGRATION SUCCESSFUL")
print("=" * 70)

print(f"Collection : {COLLECTION}")
print(f"Points     : {cloud_count}")
print("Status     : READY")
print("=" * 70)
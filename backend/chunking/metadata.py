from typing import Any


def create_chunk_metadata(
    document_metadata: dict[str, Any],
    chunks: list[str],
    chunking_method: str,
) -> list[dict[str, Any]]:
    """
    Attach metadata to each generated chunk.
    """

    if not isinstance(document_metadata, dict):
        raise TypeError("document_metadata must be a dictionary")

    if not isinstance(chunks, list):
        raise TypeError("chunks must be a list")

    if not chunking_method.strip():
        raise ValueError("chunking_method cannot be empty")

    document_id = document_metadata.get("document_id")

    if not document_id:
        raise ValueError("document_metadata must contain document_id")

    chunk_metadata = []

    for index, chunk in enumerate(chunks):
        if not isinstance(chunk, str):
            raise TypeError("each chunk must be a string")

        if not chunk.strip():
            continue

        chunk_metadata.append(
            {
                "document_id": document_id,
                "chunk_id": f"{document_id}_{index}",
                "chunk_index": index,
                "text": chunk,
                "chunking_method": chunking_method,
                "character_count": len(chunk),
                "file_name": document_metadata.get("file_name"),
                "file_type": document_metadata.get("file_type"),
            }
        )

    return chunk_metadata
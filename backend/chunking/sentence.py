import re


def sentence_chunks(
    text: str,
    max_chars: int = 500,
) -> list[str]:
    """
    Split text into sentence-aware chunks while keeping
    each chunk below the requested character limit where possible.
    """

    if not isinstance(text, str):
        raise TypeError("text must be a string")

    if max_chars <= 0:
        raise ValueError("max_chars must be greater than 0")

    text = text.strip()

    if not text:
        return []

    sentences = re.split(r"(?<=[.!?।])\s+", text)

    chunks = []
    current_chunk = ""

    for sentence in sentences:
        sentence = sentence.strip()

        if not sentence:
            continue

        if not current_chunk:
            current_chunk = sentence
            continue

        candidate = f"{current_chunk} {sentence}"

        if len(candidate) <= max_chars:
            current_chunk = candidate
        else:
            chunks.append(current_chunk)
            current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk)

    return chunks
from embeddings.embedder import Embedder


class SemanticChunker:
    def __init__(
        self,
        embedder: Embedder | None = None,
        similarity_threshold: float = 0.70,
        max_chars: int = 1000,
    ) -> None:
        if not 0 < similarity_threshold <= 1:
            raise ValueError(
                "similarity_threshold must be between 0 and 1"
            )

        if max_chars <= 0:
            raise ValueError("max_chars must be greater than 0")

        self.embedder = embedder or Embedder()
        self.similarity_threshold = similarity_threshold
        self.max_chars = max_chars

    def chunk(self, sentences: list[str]) -> list[str]:
        if not sentences:
            return []

        sentences = [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

        if not sentences:
            return []

        embeddings = self.embedder.embed_texts(sentences)

        chunks = []
        current_chunk = [sentences[0]]
        current_length = len(sentences[0])

        for index in range(1, len(sentences)):
            sentence = sentences[index]

            previous_embedding = embeddings[index - 1]
            current_embedding = embeddings[index]

            similarity = self._cosine_similarity(
                previous_embedding,
                current_embedding,
            )

            proposed_length = current_length + 1 + len(sentence)

            if (
                similarity >= self.similarity_threshold
                and proposed_length <= self.max_chars
            ):
                current_chunk.append(sentence)
                current_length = proposed_length
            else:
                chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_length = len(sentence)

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    @staticmethod
    def _cosine_similarity(
        vector_a: list[float],
        vector_b: list[float],
    ) -> float:
        dot_product = sum(
            a * b for a, b in zip(vector_a, vector_b)
        )

        magnitude_a = sum(a * a for a in vector_a) ** 0.5
        magnitude_b = sum(b * b for b in vector_b) ** 0.5

        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0

        return dot_product / (magnitude_a * magnitude_b)
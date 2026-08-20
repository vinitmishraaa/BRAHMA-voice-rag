from chunking.semantic import SemanticChunker


sentences = [
    "BRAHMA is a voice assistant.",
    "It can understand spoken commands.",
    "It uses speech recognition to convert voice into text.",
    "The Himalayas are a mountain range in Asia.",
    "Mount Everest is the highest mountain in the world.",
]


chunker = SemanticChunker(
    similarity_threshold=0.70,
    max_chars=200,
)

chunks = chunker.chunk(sentences)

print(f"Total chunks: {len(chunks)}")

for index, chunk in enumerate(chunks, start=1):
    print(f"\n--- Chunk {index} ---")
    print(chunk)
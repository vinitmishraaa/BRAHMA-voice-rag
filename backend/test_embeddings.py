from embeddings.embedder import Embedder


embedder = Embedder()

text = "BRAHMA is a voice assistant."

embedding = embedder.embed_text(text)

print("Embedding generated")
print("Dimensions:", len(embedding))
print("First 5 values:", embedding[:5])
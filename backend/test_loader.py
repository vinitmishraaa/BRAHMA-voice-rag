from ingestion.loader import load_text


text = load_text("test_document.txt")

print("Loaded document:")
print(text)
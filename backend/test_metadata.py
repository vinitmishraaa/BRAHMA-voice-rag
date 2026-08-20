from ingestion.loader import load_text
from ingestion.cleaner import clean_text
from ingestion.metadata import create_metadata


raw_text = load_text("test_document.txt")
cleaned_text = clean_text(raw_text)

metadata = create_metadata(
    "test_document.txt",
    cleaned_text,
)

print("Metadata:")
for key, value in metadata.items():
    print(f"{key}: {value}")
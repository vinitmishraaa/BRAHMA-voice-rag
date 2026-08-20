from ingestion.cleaner import clean_text


raw_text = """
BRAHMA    is a voice assistant.


This is a test document.


It contains    extra spaces.
"""


cleaned_text = clean_text(raw_text)

print("Cleaned document:")
print(cleaned_text)
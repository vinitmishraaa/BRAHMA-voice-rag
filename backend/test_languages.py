from datasets import load_dataset


dataset = load_dataset(
    "ai4bharat/MSMARCO-XI",
    split="validation",
    streaming=True,
)

languages = set()

for row in dataset:
    languages.add(
        (
            row["source_lang"],
            row["target_lang"],
        )
    )

print("Language pairs:")
for source, target in sorted(languages):
    print(f"{source} -> {target}")
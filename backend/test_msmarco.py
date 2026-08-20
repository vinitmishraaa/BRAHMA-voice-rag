from datasets import load_dataset


dataset = load_dataset(
    "ai4bharat/MSMARCO-XI",
    split="validation",
    streaming=True,
)
sample = next(iter(dataset))

print("\nColumns:")
print(dataset.column_names)

print("\nSample:")
for key, value in sample.items():
    print(f"\n--- {key} ---")
    print(type(value))
    print(value)
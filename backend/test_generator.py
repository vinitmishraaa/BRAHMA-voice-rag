from generation.generator import SLMGenerator


generator = SLMGenerator()


print("=" * 60)
print("BRAHMA HYBRID GENERATOR TEST")
print("=" * 60)


tests = [
    {
        "name": "English",
        "query": "What is a corporation?",
        "language": "english",
        "context": [
            (
                "McDonald's Corporation is one of the most "
                "recognizable corporations in the world. "
                "A corporation is a company or group of "
                "people authorized to act as a single entity "
                "(legally a person) and recognized as such "
                "in law."
            )
        ],
    },
    {
        "name": "Hindi",
        "query": "कॉरपोरेशन क्या है?",
        "language": "hindi",
        "context": [
            (
                "मैकडॉनल्ड कॉर्पोरेशन दुनिया के सबसे "
                "पहचानने योग्य निगमों में से एक है। "
                "एक निगम एक कंपनी या लोगों का समूह है "
                "जो एक एकल इकाई के रूप में कार्य करने "
                "के लिए अधिकृत है और कानून में इस तरह "
                "से मान्यता प्राप्त है।"
            )
        ],
    },
    {
        "name": "Hinglish",
        "query": "corporation kya hota hai?",
        "language": "hinglish",
        "context": [
            (
                "A corporation is a company or group of "
                "people authorized to act as a single entity "
                "and recognized as such in law."
            )
        ],
    },
    {
        "name": "Insufficient Context",
        "query": "Who is the president of France?",
        "language": "english",
        "context": [
            (
                "A corporation is a company or group of "
                "people authorized to act as a single entity."
            )
        ],
    },
]


for index, test in enumerate(
    tests,
    start=1,
):

    print("\n" + "=" * 60)
    print(
        f"Test {index}: {test['name']}"
    )

    answer = generator.generate(
        query=test["query"],
        context=test["context"],
        language=test["language"],
    )

    print("Query:")
    print(test["query"])

    print("Answer:")
    print(answer)


print("\n" + "=" * 60)
print("Hybrid generator test complete")
print("=" * 60)
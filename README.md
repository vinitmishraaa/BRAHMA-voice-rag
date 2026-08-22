BRAHMA — Voice RAG

BRAHMA is a multilingual, voice-enabled Retrieval-Augmented Generation (RAG) system that converts spoken queries into text, retrieves relevant knowledge from a vector database, and returns grounded answers from the retrieved context.

The system combines Sarvam AI Speech-to-Text, Sentence Transformers, Qdrant vector search, multilingual query routing, and deterministic answer extraction.

Voice / Text Query
        ↓
   Speech-to-Text
        ↓
 Language Detection
        ↓
 Query Embedding
        ↓
  Qdrant Retrieval
        ↓
 Relevance Filtering
        ↓
 Grounded Answer

---

✨ Key Features

🎙️ Voice Input

BRAHMA supports voice-based querying directly from the web interface.

The frontend:

- Detects available microphone devices.
- Requests microphone permission.
- Records audio using the browser's "MediaRecorder" API.
- Sends recorded audio to the backend.
- Displays the transcription.
- Processes the transcribed query through the RAG pipeline.
- Displays the retrieved context and final answer.

Text queries are also supported.

---

🗣️ Sarvam AI Speech-to-Text

Voice queries are converted into text using Sarvam AI.

The backend exposes:

POST /api/v1/transcribe

The current STT configuration uses:

Model: saaras:v3
Mode: transcribe

The audio is received by the FastAPI backend and passed to the Sarvam transcription service before entering the retrieval pipeline.

---

🌐 Multilingual RAG

BRAHMA is designed for multilingual retrieval using the AI4Bharat MSMARCO-XI dataset.

The current indexed content supports:

- English
- Hindi
- Bengali
- Gujarati

The system also supports Hinglish-style queries at query time.

For example:

corporation kya hota hai?

The query can be routed toward the appropriate multilingual retrieval languages instead of requiring a separate Hinglish dataset.

---

🧠 Embedding Model

BRAHMA uses the following Sentence Transformers model for generating embeddings:

sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

Embedding Dimension

384

The same embedding model is used for both:

- Indexed document/chunk embeddings
- User query embeddings

This allows the query vector and stored document vectors to exist in the same vector space for semantic similarity search.

---

🔎 Vector Retrieval with Qdrant

BRAHMA uses Qdrant as its vector database.

The configured collection is:

brahma_msmarco

Current retrieval configuration:

Vector Dimension:       384
Top-K Results:          3
Similarity Threshold:   0.60

The retrieval process is:

User Query
    ↓
Sentence Transformer
    ↓
384D Query Vector
    ↓
Qdrant Similarity Search
    ↓
Top-K Relevant Passages
    ↓
Similarity Filtering

Retrieved results include metadata associated with the source passage, allowing the system to preserve the relationship between the query, retrieved content, and answer.

---

📚 Dataset

BRAHMA uses the AI4Bharat MSMARCO-XI dataset as its primary retrieval dataset.

The ingestion pipeline processes dataset passages before indexing them into Qdrant.

The overall indexing flow is:

MSMARCO-XI Dataset
        ↓
Passage Selection
        ↓
Sentence-Based Chunking
        ↓
Embedding Generation
        ↓
Qdrant Vector Index

The project does not use the example MSMARCO sample approach described in the reference README. The current implementation uses the project's actual MSMARCO-XI ingestion and indexing pipeline.

---

✂️ Sentence-Based Chunking

BRAHMA currently uses sentence-based chunking rather than multiple experimental chunking strategies.

Current configuration:

Chunk Size:       500 characters
Chunk Overlap:     50 characters

The purpose of sentence-based chunking is to keep retrieved context focused while retaining enough surrounding information for meaningful semantic retrieval.

The chunking stage happens before embedding generation and Qdrant indexing.

---

🎯 Grounded Answering

BRAHMA currently follows a deterministic retrieval-and-answer pipeline.

It does not use an LLM or SLM for free-form answer generation in the current implementation.

Instead:

Query
  ↓
Language Detection
  ↓
Query Embedding
  ↓
Qdrant Retrieval
  ↓
Similarity Filtering
  ↓
Relevant Context
  ↓
Deterministic Answer Extraction
  ↓
Grounded Response

If sufficient relevant information cannot be retrieved, the system can return a fallback response rather than producing an unsupported answer.

Default fallback:

I don't have enough information to answer that.

This keeps the current system focused on retrieval-grounded and deterministic responses.

---

🛡️ Retrieval Confidence

BRAHMA uses a configurable similarity threshold to determine whether retrieved information is sufficiently relevant.

Current threshold:

0.60

Retrieved results below the configured relevance requirement are not treated as reliable grounding context.

The API response also exposes retrieval-related information that can be used by the frontend for transparency and debugging.

---

⚡ Latency Tracking

The backend measures latency across different stages of the RAG pipeline.

Tracked stages include:

Language Detection
Query Embedding
Qdrant Retrieval
Context Extraction
Answer Processing
Total Pipeline Latency

The frontend displays the resulting response latency to the user.

The system is designed to make latency measurable rather than relying on hard-coded performance claims.

Actual latency depends on:

- Network conditions
- Sarvam API response time
- Embedding model execution
- Qdrant performance
- Dataset/index size
- Hardware

---

🖥️ Frontend

The frontend is built using:

- React
- Vite
- Framer Motion
- Lucide React
- Browser "MediaRecorder" API

The interface provides a voice-first RAG experience.

🎤 Voice Console

Users can:

- Select a microphone.
- Start recording.
- Stop recording.
- View recording duration.
- Submit voice queries.
- Submit text queries.

📡 Backend Status

The frontend checks the FastAPI health endpoint to determine whether the backend is available.

💬 Answer Panel

The result interface displays information including:

- User query
- Detected language
- Retrieved context
- Grounded answer
- Retrieval confidence
- Response latency

🔄 Pipeline Visualization

The interface visualizes the major processing stages:

01  Voice       → Speech-to-Text
02  Language    → Language Detection
03  Retrieve    → Qdrant Search
04  Ground     → Relevant Context
05  Answer      → Deterministic Extraction

---

⚙️ Backend

The backend is implemented using FastAPI.

Important API routes include:

GET  /
GET  /health
POST /api/v1/query
POST /api/v1/transcribe

---

Query API

POST /api/v1/query

Example request:

{
  "query": "What is a corporation?"
}

The response contains information such as:

success
query
language
retrieval_languages
answer
sources
retrieval_confidence
latency

---

Health API

GET /health

Used by the frontend to verify backend availability.

---

🏗️ System Architecture

                         ┌──────────────────────┐
                         │     React + Vite     │
                         │      Frontend        │
                         └──────────┬───────────┘
                                    │
                              Voice / Text
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │       FastAPI        │
                         │       Backend        │
                         └──────────┬───────────┘
                                    │
                         ┌──────────▼───────────┐
                         │     Sarvam AI        │
                         │    Speech-to-Text    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │  Language Detection  │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Sentence           │
                         │   Transformers       │
                         │      384D            │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │       Qdrant         │
                         │   Vector Retrieval   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Relevance Filtering  │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Deterministic Answer │
                         │      Extraction      │
                         └──────────┬───────────┘
                                    │
                                    ▼
                              Grounded Answer

---

📁 Repository Structure

BRAHMA/
│
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── requirements.txt
│   ├── pipeline.py
│   │
│   ├── api/
│   │   └── routes.py
│   │
│   ├── embeddings/
│   │   └── embedder.py
│   │
│   ├── retrieval/
│   │   └── qdrant.py
│   │
│   ├── ingestion/
│   │   └── msmarco.py
│   │
│   ├── chunking/
│   │   └── sentence.py
│   │
│   └── indexer.py
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   │
│   └── src/
│       ├── App.jsx
│       ├── api.js
│       ├── index.css
│       │
│       ├── components/
│       │   ├── Background.jsx
│       │   ├── Navbar.jsx
│       │   ├── MicSelector.jsx
│       │   ├── VoiceButton.jsx
│       │   ├── LatencyBadge.jsx
│       │   ├── AnswerPanel.jsx
│       │   └── Pipeline.jsx
│       │
│       └── hooks/
│           └── useMicrophone.js
│
├── data/
│   └── ...
│
├── .env
├── .gitignore
└── README.md

---

🚀 Getting Started

Prerequisites

Make sure the following are installed:

- Python 3.10+
- Node.js
- npm
- Qdrant
- Sarvam AI API credentials

---

1. Clone the Repository

git clone <your-repository-url>
cd BRAHMA

---

2. Create a Python Virtual Environment

Windows

python -m venv .venv
.venv\Scripts\activate

Linux / macOS

python3 -m venv .venv
source .venv/bin/activate

---

3. Install Backend Dependencies

pip install -r backend/requirements.txt

The backend uses the project's configured dependencies for:

- FastAPI
- Uvicorn
- Qdrant
- Sentence Transformers
- Sarvam AI
- Hugging Face datasets
- Pydantic
- NumPy
- PyTorch

---

4. Configure Environment Variables

Create a ".env" file containing the required credentials and configuration.

Example:

SARVAM_API_KEY=your_sarvam_api_key

QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key

Keep all credentials private and never commit them to the repository.

---

5. Prepare the Vector Database

Run the project's ingestion/indexing pipeline to prepare the Qdrant collection.

The indexing process is:

MSMARCO-XI
    ↓
Sentence Chunking
    ↓
Embedding Generation
    ↓
Qdrant Indexing

The configured collection is:

brahma_msmarco

---

6. Install Frontend Dependencies

cd frontend
npm install

Start the frontend:

npm run dev

---

🔌 Frontend API Configuration

The frontend can use:

VITE_API_BASE_URL=http://localhost:8000

If the variable is not configured, the frontend uses:

http://localhost:8000

The frontend communicates with:

GET  /health
POST /api/v1/query
POST /api/v1/transcribe

---

🧪 Testing

The repository contains backend scripts for testing dataset ingestion and retrieval.

For example:

python test_msmarco.py

Retrieval testing can be used to verify that the indexed Qdrant collection returns relevant passages for sample queries.

A retrieval result can contain information such as:

Score
Content Language
Query ID
Retrieved Text

---

🔐 Environment & Security

Keep sensitive configuration outside version control.

Do not commit:

.env
.venv/
__pycache__/
node_modules/
API keys
Qdrant credentials
Sarvam credentials

Recommended ".gitignore" entries:

.env
.venv/
__pycache__/
node_modules/
*.pyc

---

📌 Technical Configuration

Component| Implementation
Frontend| React + Vite
UI Animation| Framer Motion
Icons| Lucide React
Backend| FastAPI
Speech-to-Text| Sarvam AI
STT Model| "saaras:v3"
Embedding Framework| Sentence Transformers
Embedding Model| "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
Embedding Dimension| 384
Vector Database| Qdrant
Qdrant Collection| "brahma_msmarco"
Dataset| AI4Bharat MSMARCO-XI
Chunking| Sentence-based
Chunk Size| 500 characters
Chunk Overlap| 50 characters
Default Top-K| 3
Retrieval Threshold| 0.60
Answer Strategy| Deterministic / Extractive
LLM Generation| Not used in current pipeline
TTS| Not used in current pipeline

---

🧭 Design Philosophy

BRAHMA focuses on making voice RAG grounded, measurable, and transparent.

The current implementation does not rely on an LLM to freely generate answers from retrieved content.

Instead, the system prioritizes:

- Semantic retrieval
- Multilingual query handling
- Explicit source context
- Retrieval confidence
- Deterministic answer extraction
- Stage-level latency measurement

This makes it easier to understand what the system retrieved and why a response was produced.

---

🔮 Future Improvements

Possible future improvements include:

- Improved multilingual language detection
- Retrieval reranking
- More advanced answer extraction
- Streaming voice interaction
- Expanded multilingual evaluation
- Retrieval benchmarking
- Improved latency analytics
- Production deployment
- Additional datasets and knowledge sources

---

👥 BRAHMA — Voice RAG

BRAHMA brings together:

React
   +
FastAPI
   +
Sarvam AI
   +
Sentence Transformers
   +
Qdrant
   +
AI4Bharat MSMARCO-XI

Voice in. Knowledge retrieved. Answers grounded.
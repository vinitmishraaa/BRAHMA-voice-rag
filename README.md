<div align="center">

# 🧠 BRAHMA — Voice RAG

### Voice In • Knowledge Retrieved • Answers Grounded

<p>
  <img src="https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=111827" alt="React" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Qdrant-FF4F64?style=for-the-badge" alt="Qdrant" />
  <img src="https://img.shields.io/badge/Sarvam%20AI-111827?style=for-the-badge" alt="Sarvam AI" />
  <img src="https://img.shields.io/badge/RAG-6A1B9A?style=for-the-badge" alt="RAG" />
</p>

<i>A multilingual, voice-enabled Retrieval-Augmented Generation system built around speech-to-text, semantic search and grounded answers.</i>

</div>

---

## 🚀 About BRAHMA

**BRAHMA** is a multilingual, voice-enabled RAG system that converts spoken questions into text, retrieves relevant knowledge from a vector database, and returns a grounded response.

The current pipeline combines **Sarvam AI Speech-to-Text**, **Sentence Transformers**, **Qdrant vector search**, multilingual query routing and deterministic answer extraction. The current implementation intentionally does **not** use an LLM/SLM for free-form answer generation.

## ✨ Key Features

| Feature | Description |
|---|---|
| 🎙️ **Voice Queries** | Record questions directly from the browser. |
| ⌨️ **Text Queries** | Submit normal text questions as well. |
| 🗣️ **Speech-to-Text** | Converts voice input using Sarvam AI `saaras:v3`. |
| 🌐 **Multilingual Retrieval** | Supports English, Hindi, Bengali and Gujarati content. |
| 🧠 **Semantic Embeddings** | Uses multilingual MiniLM embeddings with 384 dimensions. |
| 🔎 **Qdrant Search** | Retrieves relevant passages from the vector database. |
| 🛡️ **Confidence Filtering** | Uses a configurable similarity threshold of `0.60`. |
| 🎯 **Grounded Answers** | Uses deterministic extraction rather than unsupported generation. |
| ⚡ **Latency Tracking** | Tracks major stages of the RAG pipeline. |
| 📡 **Backend Health** | Frontend checks FastAPI health status. |
| 🔄 **Pipeline Visualization** | Shows the major processing stages in the UI. |

## 🧩 How It Works

```text
🎤 Voice / Text Query
          ↓
   🗣️ Speech-to-Text
          ↓
   🌐 Language Detection
          ↓
   🧠 Query Embedding
          ↓
   🔎 Qdrant Retrieval
          ↓
   🛡️ Relevance Filtering
          ↓
   📚 Relevant Context
          ↓
   🎯 Answer Extraction
          ↓
   ✅ Grounded Answer
```

## 🌐 Multilingual RAG

BRAHMA uses the **AI4Bharat MSMARCO-XI** dataset as its primary retrieval source.

Current indexed languages include:

- English
- Hindi
- Bengali
- Gujarati

The query layer can also handle Hinglish-style questions such as:

```text
corporation kya hota hai?
```

The system is designed to route multilingual queries toward relevant indexed content without requiring a separate Hinglish dataset.

## 🧠 Embedding & Retrieval

**Embedding model:**

```text
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

**Embedding dimension:** `384`

Current Qdrant configuration:

```text
Collection:          brahma_msmarco
Vector Dimension:    384
Top-K:               3
Threshold:           0.60
```

## 📚 Data Pipeline

```text
AI4Bharat MSMARCO-XI
          ↓
   Passage Selection
          ↓
 Sentence-Based Chunking
          ↓
  Embedding Generation
          ↓
     Qdrant Index
```

Current chunking configuration:

- Chunk size: **500 characters**
- Overlap: **50 characters**

## 🎯 Grounded Answering

BRAHMA follows a deterministic retrieval-and-answer pipeline:

```text
Query → Language Detection → Embedding → Qdrant Search
     → Similarity Filtering → Relevant Context → Extraction
```

If sufficient relevant information cannot be retrieved, the system can fall back to:

> I don't have enough information to answer that.

This keeps the current system focused on retrieval-grounded responses.

## ⚡ Latency Tracking

BRAHMA measures latency across stages including:

- Language detection
- Query embedding
- Qdrant retrieval
- Context extraction
- Answer processing
- Total pipeline latency

Actual latency depends on network conditions, API response time, model execution, Qdrant performance and hardware.

## 🖥️ Frontend

Built with:

- React
- Vite
- Framer Motion
- Lucide React
- Browser MediaRecorder API

The interface includes voice controls, microphone selection, recording, transcription, answer display, retrieval information, latency metrics, backend status and pipeline visualization.

## ⚙️ Backend

The backend is built with **FastAPI**.

### API Routes

```text
GET  /
GET  /health
POST /api/v1/query
POST /api/v1/transcribe
```

### Query Example

```json
{
  "query": "What is a corporation?"
}
```

Responses can include the query, detected language, retrieval languages, answer, sources, retrieval confidence and latency information.

## 🏗️ Architecture

```text
                         ┌─────────────────────┐
                         │    React + Vite     │
                         │      Frontend       │
                         └──────────┬──────────┘
                                    │
                              Voice / Text
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │       FastAPI       │
                         │       Backend       │
                         └──────────┬──────────┘
                                    │
                     ┌──────────────┼──────────────┐
                     ▼              ▼              ▼
                Sarvam AI     Language Route   Embeddings
                     │              │              │
                     └──────────────┼──────────────┘
                                    ▼
                              Qdrant Search
                                    │
                                    ▼
                           Relevance Filtering
                                    │
                                    ▼
                         Deterministic Extraction
                                    │
                                    ▼
                              Grounded Answer
```

## 📁 Repository Structure

```text
BRAHMA-voice-rag/
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── pipeline.py
│   ├── requirements.txt
│   ├── api/
│   ├── embeddings/
│   ├── retrieval/
│   ├── ingestion/
│   ├── chunking/
│   └── indexer.py
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   └── src/
│       ├── App.jsx
│       ├── api.js
│       ├── index.css
│       ├── components/
│       └── hooks/
│
├── data/
├── .gitignore
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js
- npm
- Qdrant
- Sarvam AI API credentials

### Backend

```bash
git clone https://github.com/vinitmishraaa/BRAHMA-voice-rag.git
cd BRAHMA-voice-rag
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r backend/requirements.txt
```

### Environment Variables

Create a `.env` file with the required credentials:

```env
SARVAM_API_KEY=your_sarvam_api_key
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
```

Never commit API keys or private credentials.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Example API configuration:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## 🧪 Testing & Evaluation

Retrieval tests can be used to verify that the indexed Qdrant collection returns relevant passages for sample queries. A production version should additionally benchmark retrieval recall, answer grounding, multilingual performance and end-to-end latency.

## 🔐 Security Notes

Keep the following out of version control:

```text
.env
.venv/
__pycache__/
node_modules/
API keys
Qdrant credentials
Sarvam credentials
```

## 📌 Technical Configuration

| Component | Current Implementation |
|---|---|
| Frontend | React + Vite |
| Backend | FastAPI |
| Speech-to-Text | Sarvam AI |
| STT Model | `saaras:v3` |
| Embeddings | Sentence Transformers |
| Embedding Model | `paraphrase-multilingual-MiniLM-L12-v2` |
| Embedding Dimension | 384 |
| Vector Database | Qdrant |
| Dataset | AI4Bharat MSMARCO-XI |
| Chunking | Sentence-based |
| Chunk Size | 500 characters |
| Chunk Overlap | 50 characters |
| Top-K | 3 |
| Retrieval Threshold | 0.60 |
| Answer Strategy | Deterministic / Extractive |
| LLM Generation | Not used in current pipeline |
| TTS | Not used in current pipeline |

## 🔮 Future Scope

BRAHMA can evolve into a much more capable multilingual voice knowledge assistant through:

- 🤖 **LLM-based Answer Generation** — introduce an LLM after retrieval while preserving source grounding and confidence checks.
- 🎯 **Reranking** — add a cross-encoder/reranker stage to improve retrieval precision.
- 🗣️ **More Indian Languages** — expand indexed content and evaluation coverage.
- 🎙️ **Streaming Voice Interaction** — support near-real-time speech input.
- 🔊 **Text-to-Speech** — return spoken answers for a complete voice-first experience.
- 📚 **Multiple Knowledge Sources** — connect PDFs, websites, documents and domain-specific databases.
- 📊 **RAG Evaluation** — add automated retrieval and answer-quality benchmarks.
- ⚡ **Performance Optimization** — caching, batching and optimized vector retrieval.
- ☁️ **Production Deployment** — deploy with monitoring and scalable infrastructure.
- 🧠 **Domain-Specific Assistants** — adapt BRAHMA for education, government, agriculture, enterprise knowledge and other domains.

### 🎯 Long-Term Vision

```text
Speak
  ↓
Understand
  ↓
Retrieve
  ↓
Verify
  ↓
Answer
  ↓
Speak Back
```

---

<div align="center">

### 🧠 BRAHMA — Voice RAG

<i>Multilingual voice queries • Semantic retrieval • Grounded answers</i>

</div>

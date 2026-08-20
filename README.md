# BRAHMA — Voice RAG

BRAHMA is a voice-first multilingual Retrieval-Augmented Generation (RAG) system designed to answer user queries through voice or text using relevant retrieved knowledge.

## Features

- Voice and text-based queries
- Speech-to-Text using Sarvam AI
- Multilingual query support
- Hinglish query handling
- Semantic search using Sentence Transformers
- 384-dimensional multilingual embeddings
- Qdrant vector database
- Language-aware retrieval
- Relevance filtering and deduplication
- Grounded answers based on retrieved context
- Source and retrieval-confidence information
- Stage-level latency measurement
- React-based interactive frontend
- FastAPI backend
- Multilingual retrieval evaluation

## Architecture

```text
Voice / Text
     ↓
Sarvam Speech-to-Text
     ↓
Language Detection
     ↓
Multilingual Embedding
     ↓
Qdrant Vector Search
     ↓
Relevance Filtering
     ↓
Grounded Context
     ↓
Answer

# BRAHMA Voice RAG — React Frontend

## Run

```bash
npm install
cp .env.example .env
npm run dev
```

The frontend defaults to `http://localhost:8000`.

## Current API contract expected by the frontend

### GET /api/health
Any 2xx JSON response means the backend is shown as online.

### POST /api/transcribe
Multipart form-data:
- `audio`: recorded WebM audio
- `device_id`: selected browser microphone ID (optional)

Expected JSON:
```json
{ "text": "transcribed question" }
```

### POST /api/query
JSON:
```json
{
  "question": "What is ...?",
  "conversation_id": null
}
```

Expected JSON:
```json
{
  "answer": "Grounded answer...",
  "latency_ms": 842,
  "conversation_id": "optional-id",
  "sources": [
    {
      "title": "document.pdf",
      "snippet": "relevant passage...",
      "score": 0.91,
      "page": 4,
      "url": "optional"
    }
  ]
}
```

If your existing FastAPI routes use different paths or field names, change `src/api.js` and/or the mapping in `src/App.jsx`. Once the backend files are shared, these can be aligned exactly.

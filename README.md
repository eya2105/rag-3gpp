# 3GPP RAG Chat

A Streamlit chat application for grounded questions about 3GPP TS 23.501 and
TS 24.501. It uses LangChain orchestration, Hugging Face embeddings, FAISS
semantic retrieval, Groq generation, and SQLite conversation persistence.

## Features

- Persistent chat conversations and messages in SQLite
- Conversation selector and one-click new conversations
- FAISS vector retrieval over 6,129 3GPP chunks
- Citations and source excerpts beneath every assistant answer
- Dockerized deployment with persisted data and embedding caches
- Responsive white interface

## Requirements

- Docker Desktop or Docker Engine
- Docker Compose
- A Groq API key

## Quick start with Docker

1. Copy the environment template:

   ```powershell
   Copy-Item .env.example .env
   ```

2. Set `GROQ_API_KEY` in `.env`.

3. Build and start the application:

   ```powershell
   docker compose up --build
   ```

4. Open http://localhost:8501.

On the first start, the container downloads the specifications, extracts and
chunks them, downloads the embedding model, and builds the FAISS index.

Stop the application:

```powershell
docker compose down
```

This Compose setup uses bind-mounted local directories. To remove application
data, stop the container and delete `data/`, `storage/`, and
`huggingface-cache/` explicitly.

The Compose setup binds these local directories:

- `data/` — downloaded specifications, processed chunks, and SQLite database
- `storage/` — FAISS index
- `huggingface-cache/` — downloaded embedding model cache

Because `huggingface-cache/` is local runtime data, add it to `.gitignore` if
it should remain excluded from Git.

## Local development

Create a virtual environment and install dependencies:

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add the Groq API key:

```text
GROQ_API_KEY=your-groq-api-key
```

Download and process the corpus:

```powershell
python scripts/download_specs.py
python scripts/build_chunks.py
python scripts/build_index.py
```

Start the interface:

```powershell
python -m streamlit run app.py
```

Open http://localhost:8501.

## Validation

Verify the corpus:

```powershell
python scripts/verify_chunks.py
```

Query from the terminal:

```powershell
python scripts/query_specs.py "What is the 5G system architecture?"
```

## Docker management

Rebuild after Python or dependency changes:

```powershell
docker compose up --build
```

View logs:

```powershell
docker compose logs -f rag-3gpp
```

Open a shell in the running container:

```powershell
docker compose exec rag-3gpp bash
```

## Security

Never commit `.env`, API keys, downloaded credentials, or database backups.
The repository ignores `.env`, raw data, processed data, and storage by
default. Rotate any key that is accidentally exposed.

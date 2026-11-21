# Corpus

Downloaded: 2026-11-20
Source: https://www.3gpp.org/ftp/Specs/archive/

| Spec | Release | Version | Filename | Purpose |
|---|---|---|---|---|
| 3GPP TS 23.501 | Rel-18 | **V18.12.0** | 23501-ic0.zip | Stage 2 — 5GS architecture |
| 3GPP TS 24.501 | Rel-18 | **V18.14.0** | 24501-ie0.zip | Stage 3 — NAS protocol (5GMM/5GSM) |

Both documents are English, normative, and taken from the 3GPP archive at the URLs above.
They form a complementary pair: 23.501 defines *what* the system does, 24.501 defines
*how* it is signalled between UE and network.

## Chunking summary (Step 2 ( chunking ) output)

| Spec | Sections | Chunks | Median | Max |
|---|---|---|---|---|
| TS 23.501 | 844 | 2 306 | 214 words | 250 words |
| TS 24.501 | 1 103 | 3 823 | 218 words | 250 words |

Chunking is structural: one chunk per section, sub-split at 250 rendered words
when a section is longer. Every chunk carries {spec, release, version, section,
title, breadcrumb}. Tables split by row with header repetition; abbreviation
lists split between entries.

## Groq query

Set a local `.env` entry before querying the corpus:

```text
GROQ_API_KEY=your-groq-key
```

The key may also be stored as `API_KEY`. The default model is
`qwen/qwen3.8-27b`, and the Groq OpenAI-compatible base URL is
`https://api.groq.com/openai/v1`. Run:

```powershell
python scripts/build_index.py
python scripts/query_specs.py "What is the 5G system architecture?"
python scripts/query_specs.py "Explain 5GMM cause value" --limit 5
```

## Streamlit interface

Start the local interface after building the FAISS index:

```powershell
python scripts/build_index.py
python -m streamlit run app.py
```

The key must not be committed to Git or placed directly in source files.

## Chat persistence

Streamlit conversations and messages are stored in `data/conversations.db`.
Selecting a conversation restores its transcript; submitting a prompt without
a selection creates a conversation automatically.
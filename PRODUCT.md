# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Telecom engineers and researchers working with 3GPP specifications.

## Product Purpose

Answer technical questions using the ingested 3GPP corpus and cite the retrieved
specification sections supporting each answer.

## Positioning

A focused 3GPP RAG interface that combines semantic retrieval with grounded
generation and visible source citations.

## Operating Context

Users enter technical questions and adjust the number of retrieved chunks.
Results should remain traceable to TS 23.501 and TS 24.501.

## Capabilities and Constraints

- Use a persisted FAISS index.
- Use LangChain orchestration and Groq generation.
- Show chunk IDs and source section metadata.
- Keep the interface minimal and use a white visual system.
- Do not claim external product branding.

## Evidence on Hand

- 6,129 indexed chunks from 3GPP TS 23.501 and TS 24.501.
- A validated local chunking and ingestion pipeline.

## Product Principles

- Ground answers in retrieved context.
- Make source provenance visible.
- Keep controls secondary to the question and answer.

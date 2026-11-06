# ModuleAtlas Development & Research Log

### Objective

Initialise the ModuleAtlas backend and establish a reproducible project structure.

### Implementation

- Created the ModuleAtlas Git repository.
- Created separate backend, research, and documentation areas.
- Standardised the backend on Python 3.12.
- Added dependency management using uv.
- Added FastAPI.
- Created the initial API application.
- Added a `/health` endpoint.
- Confirmed automatic OpenAPI/Swagger documentation.

### Current Architecture

Client → FastAPI → API Route → JSON Response

### Research Notes

No retrieval or generative AI functionality has been introduced yet.

This initial version provides the software foundation on which later baseline and experimental retrieval approaches will be implemented and evaluated.

### Chat API Baseline

Implemented the initial `/api/v1/chat` endpoint using typed Pydantic request and response models.

The current chat service uses a deterministic placeholder response and contains no LLM or retrieval functionality.

This establishes a baseline API workflow that can be tested independently before introducing generative or retrieval-based components.

Current request flow:

Client → FastAPI → Pydantic Validation → Chat Service → Typed Response

### LLM Provider Abstraction

Introduced an abstract LLM service interface so that ModuleAtlas is not coupled to a specific foundation model provider.

A deterministic mock implementation is currently used while AWS Bedrock account verification is pending.

The abstraction standardises generation output using:

- generated text
- model identifier
- input token count
- output token count
- inference latency

This design will allow different foundation models and configurations to be evaluated without changing the surrounding application architecture.

### Configuration and Provider Selection

Moved runtime configuration outside application code using typed
Pydantic settings.

The LLM provider, AWS region, AWS profile, and Bedrock model identifier
are now externally configurable.

Introduced an LLM factory that selects the provider implementation from
runtime configuration.

This allows model/provider configurations to be changed without modifying
the surrounding application logic, supporting repeatable comparative
experiments.

### PDF Ingestion Baseline

Implemented native PDF text extraction using PyMuPDF.

Documents are processed page-by-page while preserving:

- document filename
- SHA-256 document fingerprint
- one-based page number
- extracted page text
- page count

No OCR, chunking, embeddings, retrieval, or generative AI are
included in the current ingestion baseline.

Text extraction currently uses PyMuPDF native text extraction with
coordinate-based sorting enabled.

This establishes a provenance-preserving document representation for
later retrieval and citation experiments.
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

### Initial Extraction Quality Observation

Testing against `L4_W5_Connectivity.pdf` demonstrated that the
presence of extracted text is not sufficient to determine successful
page extraction.

All 18 pages contained some native text, producing a nominal extraction
rate of 100%. However, several visually rich slides contain diagrams,
tables, or graphical information for which only the page heading or a
small amount of text is available through native PDF text extraction.

Therefore, subsequent ingestion evaluation will distinguish between
empty pages, sparse pages, and text-rich pages rather than relying only
on the presence or absence of extracted text.

This motivates investigation of enhanced extraction approaches for
visual or structurally complex academic material.

### Sparse Page Detection

A simple page-level extraction heuristic was introduced using extracted
character count.

Pages containing no extracted characters are classified as `empty`.

Pages containing between 1 and 49 characters are classified as `sparse`.

Pages containing 50 or more characters are currently classified as
`text-rich`.

On the initial Smart Systems lecture document, 7 of 18 pages were
classified as sparse.

Manual inspection indicates that several sparse pages contain substantial
visual information such as diagrams and tables despite containing little
extractable native text.

The sparse threshold is therefore treated as a triage heuristic rather
than a measure of extraction correctness. Its effectiveness will need to
be evaluated against manually reviewed pages.

### Extraction Quality Ground Truth

Created the first manually labelled extraction-quality dataset using
the Smart Systems Wireless Connectivity lecture.

Each page was reviewed to determine whether native text extraction
adequately preserved the meaningful teaching content.

Pages requiring additional processing were labelled according to
the dominant missing information type, including diagrams, tables,
and other visual content.

The initial character-count-based sparse-page heuristic will be
evaluated against this ground truth using precision, recall, and
accuracy.

Recall is considered particularly important because a false negative
allows incomplete source content to enter the downstream retrieval
pipeline.

Baseline H1 — Character-count heuristic

Threshold: < 50 characters

Precision: 1.000
Recall:    0.636
Accuracy:  0.778

F1 score:  ≈ 0.778

Specificity = TN / (TN + FP)
            = 7 / 7
            = 1.000

Meaning we correctly left all genuinely adequate pages alone.
So the heuristic is: Very conservative: when it flags something, it's right—but it misses too many visually problematic pages.

### Character Threshold Experiment

Character-count thresholds from 25 to 250 were evaluated against the
manually labelled extraction-quality dataset.

The 125-character threshold produced the strongest balanced result:

- Precision: 0.818
- Recall: 0.818
- F1: 0.818
- Accuracy: 0.778

Increasing the threshold to 200 improved recall to 0.909 but reduced
precision to 0.714.

These results indicate that character count alone presents a
precision-recall trade-off and may not reliably identify pages containing
meaningful visual information.

The 125-character threshold is retained as a development baseline rather
than a final threshold because the current evaluation contains only one
18-page document.

The next experiment introduces visual-layout signals such as embedded
image count and vector drawing count.

### Extraction Heuristic Validation

The extraction heuristics were evaluated unchanged on a second
26-page Smart Systems lecture document.

Character threshold < 50:
- Precision: 0.000
- Recall: 0.000
- F1: 0.000
- Accuracy: 0.577

Character threshold < 125:
- Precision: 0.750
- Recall: 0.273
- F1: 0.400
- Accuracy: 0.654

Multi-signal heuristic v1:
- Precision: 0.733
- Recall: 1.000
- F1: 0.846
- Accuracy: 0.846

The character-only heuristics generalised poorly because visually
significant pages could still contain substantial extracted text.

The multi-signal heuristic maintained perfect recall on the validation
document, although four false positives reduced precision.

This suggests that visual-structure features improve detection of pages
requiring enhanced extraction, but raw image and drawing counts are not
sufficient to determine whether visual content is semantically important.
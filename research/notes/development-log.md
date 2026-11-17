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

### Multi-Signal Extraction Heuristic v2

A second multi-signal heuristic was evaluated after introducing
template-filtered image metrics and vector-layout features.

Development PDF 1:
- Precision: 0.846
- Recall: 1.000
- F1: 0.917
- Accuracy: 0.889

Development PDF 2:
- Precision: 0.846
- Recall: 1.000
- F1: 0.917
- Accuracy: 0.923

Compared with multi-signal v1 on PDF 2, v2 reduced false positives
from 5 to 2 while preserving zero false negatives.

Character-count-only approaches generalised poorly, particularly on
the second document where visually significant pages frequently
contained substantial native text.

Because v2 was designed after inspecting both documents, these results
are treated as development results rather than independent validation.

A third document with a different visual/template style will be used
for validation without modifying the heuristic.

### Third-Document Validation and Vector Template Detection

A third document, `Project_Planning_Lecture.pdf`, was selected to test
the heuristic against a different module, lecturer style, and presentation
template.

The document contained 37 pages and included a mixture of:

- conventional text slides
- tables
- infographics
- mind maps
- diagrams
- timelines
- Gantt charts

Initial evaluation of the multi-signal heuristic produced:

- Precision: 0.189
- Recall: 1.000
- F1: 0.318
- Accuracy: 0.189

Although all pages requiring enhanced extraction were detected, all
30 pages that did not require enhanced extraction were incorrectly
flagged.

Inspection of the extracted PDF features showed that
`largest_drawing_cluster_coverage` was equal to `1.000` on almost every
page.

Further investigation identified a full-page white vector rectangle
repeated on all 37 pages, together with several header and decorative
vector elements repeated on 36 of 37 pages.

These repeated elements were part of the presentation template rather
than meaningful page-specific content.

This demonstrated that vector drawing features can be affected by
presentation templates in the same way as raster image features.

### Vector Template Filtering

Document-level template detection was extended to vector drawings.

Each vector drawing is represented using a lightweight signature based on:

- normalised bounding box coordinates
- drawing type
- fill colour
- line colour
- line width
- number of drawing operations

Drawing signatures appearing on at least 80% of document pages are
classified as probable template elements.

The ingestion pipeline now preserves both raw and template-filtered
drawing features:

- total drawing count
- template drawing count
- meaningful drawing count
- total drawing cluster count
- meaningful drawing cluster count
- largest raw drawing cluster coverage
- largest meaningful drawing cluster coverage

After template filtering, ordinary slides in the third document typically
contained zero meaningful drawings, while pages containing page-specific
tables, timelines and diagrams retained their visual features.

This reduced the number of false positives caused by repeated
presentation design elements.

### Small Decorative Image Filtering

Evaluation of the third document showed that image count alone was also
too sensitive.

Several normal text slides contained multiple small icons or decorative
images while containing no semantically important visual information.

Examples included pages containing several images where the largest image
covered less than approximately 1% of the page.

The multi-signal rule was therefore refined so that multiple images are
only treated as evidence of visual importance when at least one image has
a minimum page coverage.

The relevant condition became:

`meaningful_image_count >= 2 AND largest_meaningful_image_coverage >= 0.02`

This retained detection of pages containing multiple meaningful visual
elements while reducing false positives caused by small decorative
graphics.

### Refined Multi-Signal Heuristic Results

After raster template filtering, vector template filtering, and small-image
filtering, the refined multi-signal heuristic produced the following
development results.

`L4_W5_Connectivity.pdf`

- Precision: 0.917
- Recall: 1.000
- F1: 0.957
- Accuracy: 0.944

`W2_IoT systems architecture22.pdf`

- Precision: 0.917
- Recall: 1.000
- F1: 0.957
- Accuracy: 0.962

`Project_Planning_Lecture.pdf`

- Precision: 0.700
- Recall: 1.000
- F1: 0.824
- Accuracy: 0.919

The third document improved from 13 false positives to 3 while retaining
zero false negatives.

These results show that filtering document-level visual templates and
small decorative images significantly improves the precision of the
heuristic.

However, all three documents influenced the design of the heuristic and
are therefore treated as development data rather than independent
validation data.

### Unseen Holdout Evaluation

A fourth document, `Student_Service_Portal_Presentation.pdf`, was selected
as an untouched holdout document.

This presentation differed significantly from the previous documents.

It contained:

- 11 pages
- no meaningful raster images
- approximately 1,500 to 3,000 extracted characters per page
- architecture diagrams
- workflow diagrams
- entity relationships
- structured endpoint and configuration layouts
- predominantly vector-based visual content

Five pages were manually labelled as requiring enhanced extraction because
important relationships or spatial structure were not adequately
represented by native text extraction.

The frozen multi-signal heuristic was then evaluated without modification.

Results:

- TP: 1
- FP: 1
- TN: 5
- FN: 4
- Precision: 0.500
- Recall: 0.200
- F1: 0.286
- Accuracy: 0.545

Both character-count baselines achieved zero recall because every page
contained a large amount of native extractable text.

### Holdout Finding

The holdout experiment demonstrated an important limitation of the
hand-engineered extraction heuristic.

Pages can contain large amounts of correctly extracted text while still
losing important semantic relationships expressed through:

- arrows
- spatial positioning
- architecture connections
- workflows
- entity relationships
- diagram structure

The experiment also showed that visual size alone is not a reliable
indicator of semantic importance.

Some meaningful architecture and workflow diagrams occupied relatively
small areas of the page, while some visually large structured layouts
were already sufficiently represented by extracted text.

Therefore, character count, image count, drawing count, and visual
coverage cannot reliably determine whether native extraction preserves
the complete semantic meaning of every academic document.

### Extraction Baseline Decision

Further development of increasingly complex custom PDF visual heuristics
was stopped at this stage.

The current extraction pipeline will be retained as a reproducible
baseline rather than extended into a complete custom visual-document
understanding system.

The baseline now includes:

- native PyMuPDF text extraction
- SHA-256 document provenance
- page-level extraction statistics
- manually labelled extraction-quality ground truth
- raster image template filtering
- vector drawing template filtering
- meaningful image and drawing features
- character-count baselines
- multi-signal extraction heuristics
- development-set evaluation
- independent holdout evaluation
- documented failure cases

The holdout failure is intentionally retained as part of the research
evidence because it demonstrates the limitations of manually engineered
document-complexity rules.

### Future Enhanced Extraction Approach

Future experiments will compare the lightweight native-extraction baseline
against an enhanced multimodal document-processing approach using Amazon
Bedrock once Bedrock access is available.

The purpose of the comparison will not be to reproduce Bedrock document
understanding functionality manually.

Instead, ModuleAtlas will evaluate whether enhanced multimodal parsing
improves downstream:

- retrieval quality
- answer quality
- grounding
- citation accuracy
- latency
- token usage
- processing cost

This creates a more useful research comparison between a lightweight,
low-cost native extraction pipeline and a more capable managed
multimodal extraction approach.

### Extraction Phase Conclusion

The extraction investigation demonstrated that native PDF extraction is
sufficient for many text-oriented academic pages but can lose important
information when meaning depends on visual or spatial relationships.

Simple character-count heuristics generalised poorly.

Adding visual features improved detection on development documents, while
template filtering significantly reduced false positives caused by
presentation backgrounds and repeated decorative elements.

However, the independent holdout document showed that manually engineered
visual-complexity heuristics still fail on dense vector diagrams where
text extraction succeeds but structural meaning is lost.

The extraction phase is therefore considered complete as a baseline
experiment.

The next development stage will focus on document chunking, embeddings,
vector storage, retrieval, and downstream RAG evaluation rather than
further optimisation of custom PDF parsing rules.
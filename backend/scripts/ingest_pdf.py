import sys
from pathlib import Path

from app.services.document_ingestion import (
    DocumentIngestionService,
)
from app.services.extraction_analysis import (
    ExtractionAnalysisService,
)


def main() -> None:
    if len(sys.argv) != 2:
        print(
            "Usage: python -m scripts.ingest_pdf <pdf-path>"
        )
        raise SystemExit(1)

    file_path = Path(sys.argv[1])

    service = DocumentIngestionService()
    document = service.ingest_pdf(file_path)

    print(f"Document: {document.filename}")
    print(f"Document ID: {document.document_id}")
    print(f"Pages: {document.page_count}")

    print("\n--- First page preview ---\n")

    if document.pages:
        print(document.pages[0].text[:1000])
    
    analysis_service = ExtractionAnalysisService()

    stats = analysis_service.analyse(document)

    print("\n--- Extraction Stats ---\n")
    print(f"Total Pages: {stats.total_pages}")
    print(f"Pages with Text: {stats.pages_with_text}")
    print(f"Empty Pages: {stats.empty_pages}")
    print(f"Total Characters: {stats.total_characters}")
    print(f"Average Characters per Page: {stats.average_characters_per_page}")
    print(f"Sparse Pages: {stats.sparse_pages}")
    print("Minimum Characters on a Page: " f"{stats.minimum_characters_on_page}")
    print("Maximum Characters on a Page: " f"{stats.maximum_characters_on_page}")

    print("\n--- Sparse Pages ---\n")

    for page in stats.pages:
        if page.classification == "sparse":
            print(
                f"Page {page.page_number}: "
                f"{page.character_count} characters"
            )

if __name__ == "__main__":
    main()
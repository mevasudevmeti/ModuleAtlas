import sys
from pathlib import Path

from app.services.document_ingestion import (
    DocumentIngestionService,
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


if __name__ == "__main__":
    main()
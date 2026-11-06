import hashlib
from pathlib import Path

import pymupdf
from app.models.document import (
    DocumentMetadata,
    DocumentPage,
    IngestedDocument,
)
from app.models.document import DocumentPage, IngestedDocument


class DocumentIngestionService:

    def ingest_pdf(
    self,
    file_path: Path,
    metadata: DocumentMetadata | None = None,
) -> IngestedDocument:
        if not file_path.exists():
            raise FileNotFoundError(
                f"PDF not found: {file_path}"
            )

        if file_path.suffix.lower() != ".pdf":
            raise ValueError(
                f"Expected a PDF file: {file_path}"
            )

        file_hash = self._calculate_sha256(file_path)

        pages: list[DocumentPage] = []

        with pymupdf.open(file_path) as document:
            for page_index, page in enumerate(document):
                text = page.get_text(
                    "text",
                    sort=True,
                ).strip()

                pages.append(
                    DocumentPage(
                        page_number=page_index + 1,
                        text=text,
                    )
                )
        if metadata is None:
            metadata = DocumentMetadata()
            
        return IngestedDocument(
            document_id=file_hash,
            filename=file_path.name,
            sha256=file_hash,
            page_count=len(pages),
            metadata=metadata,
            pages=pages,
        )

    @staticmethod
    def _calculate_sha256(file_path: Path) -> str:
        sha256 = hashlib.sha256()

        with file_path.open("rb") as file:
            for block in iter(
                lambda: file.read(1024 * 1024),
                b"",
            ):
                sha256.update(block)

        return sha256.hexdigest()
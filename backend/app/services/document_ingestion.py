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

                image_info = page.get_image_info()
                drawings = page.get_drawings()
                drawing_clusters = page.cluster_drawings(
                    drawings=drawings
                )

                page_area = page.rect.get_area()

                largest_image_area = max(
                    (
                        pymupdf.Rect(image["bbox"]).get_area()
                        for image in image_info
                    ),
                    default=0,
                )

                largest_drawing_cluster_area = max(
                    (
                        cluster.get_area()
                        for cluster in drawing_clusters
                    ),
                    default=0,
                )

                largest_image_coverage = (
                    largest_image_area / page_area
                    if page_area > 0
                    else 0
                )

                largest_drawing_cluster_coverage = (
                    largest_drawing_cluster_area / page_area
                    if page_area > 0
                    else 0
                )

                pages.append(
                    DocumentPage(
                        page_number=page_index + 1,
                        text=text,
                        image_count=len(image_info),
                        drawing_count=len(drawings),
                        drawing_cluster_count=len(
                            drawing_clusters
                        ),
                        largest_image_coverage=round(
                            largest_image_coverage,
                            4,
                        ),
                        largest_drawing_cluster_coverage=round(
                            largest_drawing_cluster_coverage,
                            4,
                        ),
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
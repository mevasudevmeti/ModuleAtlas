import hashlib
from collections import Counter
from pathlib import Path

import pymupdf

from app.models.document import (
    DocumentMetadata,
    DocumentPage,
    IngestedDocument,
)


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

        file_hash = self._calculate_sha256(
            file_path
        )

        pages: list[DocumentPage] = []

        with pymupdf.open(file_path) as document:

            template_image_digests = (
                self._find_template_image_digests(
                    document
                )
            )

            for page_index, page in enumerate(
                document
            ):
                text = page.get_text(
                    "text",
                    sort=True,
                ).strip()

                image_info = page.get_image_info(
                    hashes=True,
                    xrefs=True,
                )

                drawings = page.get_drawings()

                drawing_clusters = (
                    page.cluster_drawings(
                        drawings=drawings
                    )
                )

                page_area = page.rect.get_area()

                template_images = [
                    image
                    for image in image_info
                    if image.get("digest")
                    in template_image_digests
                ]

                meaningful_images = [
                    image
                    for image in image_info
                    if image.get("digest")
                    not in template_image_digests
                ]

                largest_image_area = max(
                    (
                        pymupdf.Rect(
                            image["bbox"]
                        ).get_area()
                        for image in image_info
                    ),
                    default=0,
                )

                largest_meaningful_image_area = max(
                    (
                        pymupdf.Rect(
                            image["bbox"]
                        ).get_area()
                        for image in meaningful_images
                    ),
                    default=0,
                )

                largest_drawing_cluster_area = max(
                    (
                        cluster.get_area()
                        for cluster
                        in drawing_clusters
                    ),
                    default=0,
                )

                largest_image_coverage = (
                    largest_image_area
                    / page_area
                    if page_area > 0
                    else 0
                )

                largest_meaningful_image_coverage = (
                    largest_meaningful_image_area
                    / page_area
                    if page_area > 0
                    else 0
                )

                largest_drawing_cluster_coverage = (
                    largest_drawing_cluster_area
                    / page_area
                    if page_area > 0
                    else 0
                )

                pages.append(
                    DocumentPage(
                        page_number=page_index + 1,
                        text=text,

                        image_count=len(
                            image_info
                        ),

                        template_image_count=len(
                            template_images
                        ),

                        meaningful_image_count=len(
                            meaningful_images
                        ),

                        drawing_count=len(
                            drawings
                        ),

                        drawing_cluster_count=len(
                            drawing_clusters
                        ),

                        largest_image_coverage=round(
                            largest_image_coverage,
                            4,
                        ),

                        largest_meaningful_image_coverage=round(
                            largest_meaningful_image_coverage,
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
    def _find_template_image_digests(
        document: pymupdf.Document,
        repetition_ratio: float = 0.8,
    ) -> set[bytes]:

        digest_page_counts: Counter[bytes] = (
            Counter()
        )

        for page in document:

            seen_on_page: set[bytes] = set()

            images = page.get_image_info(
                hashes=True,
                xrefs=True,
            )

            for image in images:

                digest = image.get("digest")

                if digest is not None:
                    seen_on_page.add(
                        digest
                    )

            digest_page_counts.update(
                seen_on_page
            )

        minimum_pages = (
            len(document)
            * repetition_ratio
        )

        return {
            digest
            for digest, page_count
            in digest_page_counts.items()
            if page_count >= minimum_pages
        }

    @staticmethod
    def _calculate_sha256(
        file_path: Path,
    ) -> str:

        sha256 = hashlib.sha256()

        with file_path.open("rb") as file:

            for block in iter(
                lambda: file.read(
                    1024 * 1024
                ),
                b"",
            ):
                sha256.update(block)

        return sha256.hexdigest()
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

            template_drawing_signatures = (
                self._find_template_drawing_signatures(
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

                template_drawings = []
                meaningful_drawings = []

                for drawing in drawings:

                    signature = (
                        self._create_drawing_signature(
                            drawing,
                            page.rect,
                        )
                    )

                    if (
                        signature
                        in template_drawing_signatures
                    ):
                        template_drawings.append(
                            drawing
                        )
                    else:
                        meaningful_drawings.append(
                            drawing
                        )

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

                drawing_clusters = (
                    page.cluster_drawings(
                        drawings=drawings
                    )
                    if drawings
                    else []
                )

                meaningful_drawing_clusters = (
                    page.cluster_drawings(
                        drawings=meaningful_drawings
                    )
                    if meaningful_drawings
                    else []
                )

                page_area = page.rect.get_area()

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

                largest_meaningful_drawing_cluster_area = max(
                    (
                        cluster.get_area()
                        for cluster
                        in meaningful_drawing_clusters
                    ),
                    default=0,
                )

                largest_image_coverage = (
                    largest_image_area / page_area
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

                largest_meaningful_drawing_cluster_coverage = (
                    largest_meaningful_drawing_cluster_area
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

                        template_drawing_count=len(
                            template_drawings
                        ),

                        meaningful_drawing_count=len(
                            meaningful_drawings
                        ),

                        drawing_cluster_count=len(
                            drawing_clusters
                        ),

                        meaningful_drawing_cluster_count=len(
                            meaningful_drawing_clusters
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

                        largest_meaningful_drawing_cluster_coverage=round(
                            largest_meaningful_drawing_cluster_coverage,
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
    def _normalise_drawing_style(
        value,
    ):
        if value is None:
            return None

        if isinstance(
            value,
            (tuple, list),
        ):
            return tuple(
                round(
                    float(item),
                    3,
                )
                for item in value
            )

        if isinstance(
            value,
            (int, float),
        ):
            return round(
                float(value),
                3,
            )

        return str(value)

    @classmethod
    def _create_drawing_signature(
        cls,
        drawing: dict,
        page_rect: pymupdf.Rect,
    ) -> tuple:

        rect = pymupdf.Rect(
            drawing["rect"]
        )

        normalised_rect = (
            round(
                rect.x0 / page_rect.width,
                3,
            ),
            round(
                rect.y0 / page_rect.height,
                3,
            ),
            round(
                rect.x1 / page_rect.width,
                3,
            ),
            round(
                rect.y1 / page_rect.height,
                3,
            ),
        )

        return (
            normalised_rect,
            drawing.get("type"),

            cls._normalise_drawing_style(
                drawing.get("fill")
            ),

            cls._normalise_drawing_style(
                drawing.get("color")
            ),

            round(
                float(
                    drawing.get("width")
                    or 0
                ),
                2,
            ),

            len(
                drawing.get("items")
                or []
            ),
        )

    @classmethod
    def _find_template_drawing_signatures(
        cls,
        document: pymupdf.Document,
        repetition_ratio: float = 0.8,
    ) -> set[tuple]:

        signature_page_counts: Counter = (
            Counter()
        )

        for page in document:

            seen_on_page: set[tuple] = set()

            drawings = page.get_drawings()

            for drawing in drawings:

                signature = (
                    cls._create_drawing_signature(
                        drawing,
                        page.rect,
                    )
                )

                seen_on_page.add(
                    signature
                )

            signature_page_counts.update(
                seen_on_page
            )

        minimum_pages = (
            len(document)
            * repetition_ratio
        )

        return {
            signature
            for signature, page_count
            in signature_page_counts.items()
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
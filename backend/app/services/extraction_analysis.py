from app.models.document import IngestedDocument
from app.models.extraction import (
    ExtractionStats,
    PageExtractionAssessment,
)


class ExtractionAnalysisService:

    SPARSE_PAGE_THRESHOLD = 50

    def analyse(
        self,
        document: IngestedDocument,
    ) -> ExtractionStats:

        page_assessments: list[PageExtractionAssessment] = []

        for page in document.pages:
            character_count = len(page.text.strip())

            if character_count == 0:
                classification = "empty"

            elif character_count < self.SPARSE_PAGE_THRESHOLD:
                classification = "sparse"

            else:
                classification = "text-rich"

            page_assessments.append(
                PageExtractionAssessment(
                    page_number=page.page_number,
                    character_count=character_count,
                    classification=classification,
                )
            )

        total_pages = document.page_count

        pages_with_text = sum(
            1
            for page in page_assessments
            if page.character_count > 0
        )

        empty_pages = sum(
            1
            for page in page_assessments
            if page.classification == "empty"
        )

        sparse_pages = sum(
            1
            for page in page_assessments
            if page.classification == "sparse"
        )

        total_characters = sum(
            page.character_count
            for page in page_assessments
        )

        average_characters_per_page = (
            total_characters / total_pages
            if total_pages > 0
            else 0
        )

        character_counts = [
            page.character_count
            for page in page_assessments
        ]

        return ExtractionStats(
            total_pages=total_pages,
            pages_with_text=pages_with_text,
            empty_pages=empty_pages,
            sparse_pages=sparse_pages,
            total_characters=total_characters,
            average_characters_per_page=round(
                average_characters_per_page,
                2,
            ),
            minimum_characters_on_page=min(
                character_counts,
                default=0,
            ),
            maximum_characters_on_page=max(
                character_counts,
                default=0,
            ),
            pages=page_assessments,
        )
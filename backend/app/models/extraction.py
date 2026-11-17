from pydantic import BaseModel


class PageExtractionAssessment(BaseModel):
    page_number: int
    character_count: int
    image_count: int
    template_image_count: int
    meaningful_image_count: int
    drawing_count: int
    drawing_cluster_count: int
    largest_image_coverage: float
    largest_meaningful_image_coverage: float
    largest_drawing_cluster_coverage: float
    classification: str


class ExtractionStats(BaseModel):
    total_pages: int
    pages_with_text: int
    empty_pages: int
    sparse_pages: int
    total_characters: int
    average_characters_per_page: float
    minimum_characters_on_page: int
    maximum_characters_on_page: int
    pages: list[PageExtractionAssessment]
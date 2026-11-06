from pydantic import BaseModel


class PageExtractionAssessment(BaseModel):
    page_number: int
    character_count: int
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
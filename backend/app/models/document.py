from pydantic import BaseModel


class DocumentMetadata(BaseModel):
    module: str | None = None
    week: str | None = None
    title: str | None = None
    document_type: str | None = None


class DocumentPage(BaseModel):
    page_number: int
    text: str
    image_count: int
    template_image_count: int
    meaningful_image_count: int
    drawing_count: int
    drawing_cluster_count: int
    largest_image_coverage: float
    largest_meaningful_image_coverage: float
    largest_drawing_cluster_coverage: float


class IngestedDocument(BaseModel):
    document_id: str
    filename: str
    sha256: str
    page_count: int
    metadata: DocumentMetadata
    pages: list[DocumentPage]
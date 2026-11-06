from pydantic import BaseModel


class DocumentMetadata(BaseModel):
    module: str | None = None
    week: str | None = None
    title: str | None = None
    document_type: str | None = None


class DocumentPage(BaseModel):
    page_number: int
    text: str


class IngestedDocument(BaseModel):
    document_id: str
    filename: str
    sha256: str
    page_count: int
    metadata: DocumentMetadata
    pages: list[DocumentPage]
from pydantic import BaseModel


class DocumentPage(BaseModel):
    page_number: int
    text: str


class IngestedDocument(BaseModel):
    document_id: str
    filename: str
    sha256: str
    page_count: int
    pages: list[DocumentPage]
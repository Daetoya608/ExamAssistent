import io
from abc import ABC, abstractmethod

from app.domains.documents.schemas import PDFBase


class ParserInterface(ABC):
    @abstractmethod
    def get_pdf(self, file_bytes: io.BytesIO, filename: str) -> PDFBase: ...

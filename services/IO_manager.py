import os
from typing import Union

from PyPDF2 import PdfReader
from docx import Document


class IOManager:
    def __init__(self):
        pass

    def load(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        extension = os.path.splitext(file_path)[1].lower()

        if extension == ".txt":
            return self._read_txt(file_path)
        elif extension == ".pdf":
            return self._read_pdf(file_path)
        elif extension == ".docx":
            return self._read_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {extension}")

    def _read_txt(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def _read_pdf(self, file_path: str) -> str:
        text = ""
        with open(file_path, "rb") as f:
            reader = PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
        return text

    def _read_docx(self, file_path: str) -> str:
        doc = Document(file_path)
        return "\n".join(paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip())

from pathlib import Path
from pypdf import PdfReader
from docx import Document


def extract_pdf_text(file_source) -> str:
    reader = PdfReader(file_source)
    text = []

    for page in reader.pages:
        text.append(page.extract_text() or "")

    return "\n".join(text).strip()


def extract_docx_text(file_source) -> str:
    document = Document(file_source)
    paragraphs = [paragraph.text for paragraph in document.paragraphs]
    return "\n".join(paragraphs).strip()



def extract_text(file_source, filename: str | None = None) -> str:
    if filename:
        extension = Path(filename).suffix.lower()
    else:
        extension = Path(str(file_source)).suffix.lower()

    if extension == ".pdf":
        text = extract_pdf_text(file_source)
    elif extension == ".docx":
        text = extract_docx_text(file_source)
    else:
        raise ValueError("Please upload a PDF or DOCX resume.")

    if not text:
        raise ValueError(
            "No readable text was found. The file may be empty or image-based."
        )

    return text



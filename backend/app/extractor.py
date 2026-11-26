
from pathlib import Path
from pypdf import PdfReader


def extract_pdf_text(pdf_path: str) -> str:
    """
    Extract text from a PDF file page by page.
    """

    file_path = Path(pdf_path)

    if not file_path.exists():
        raise FileNotFoundError(f"PDF not found: {file_path}")

    if file_path.suffix.lower() != ".pdf":
        raise ValueError("The provided file must be a PDF.")

    reader = PdfReader(str(file_path))

    extracted_pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text()

        if page_text and page_text.strip():
            extracted_pages.append(
                f"\n--- Page {page_number} ---\n{page_text.strip()}"
            )

    if not extracted_pages:
        raise ValueError(
            "No readable text found in the PDF. "
            "It may require OCR."
        )

    return "\n".join(extracted_pages)


def extract_document(pdf_path: str) -> dict:
    """
    Extract text and basic metadata from a PDF.
    """

    text = extract_pdf_text(pdf_path)

    return {
        "file_name": Path(pdf_path).name,
        "text": text,
        "character_count": len(text),
        "word_count": len(text.split())
    }

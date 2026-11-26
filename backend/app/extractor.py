
from pathlib import Path
from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}


def extract_text(file_path: str) -> str:
    path = Path(file_path)
    extension = path.suffix.lower()

    if extension == ".pdf":
        reader = PdfReader(str(path))
        pages = []

        for page in reader.pages:
            pages.append(page.extract_text() or "")

        return "\n".join(pages)

    if extension in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore")

    raise ValueError(f"Unsupported file type: {extension}")

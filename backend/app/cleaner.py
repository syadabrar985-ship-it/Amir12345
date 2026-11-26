
import re
import unicodedata


def clean_text(text: str) -> str:
    """
    Clean extracted PDF text.
    """

    if not isinstance(text, str):
        raise TypeError("Input must be a string.")

    text = unicodedata.normalize("NFKC", text)

    text = text.replace("\x00", " ")
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    text = re.sub(r"[ \t]+", " ", text)

    text = re.sub(r" *\n *", "\n", text)

    text = re.sub(r"\n{3,}", "\n\n", text)

    text = text.strip()

    return text


def clean_document(document: dict) -> dict:
    """
    Clean extracted document text while preserving metadata.
    """

    if "text" not in document:
        raise ValueError("Document does not contain extracted text.")

    cleaned_text = clean_text(document["text"])

    if not cleaned_text:
        raise ValueError("Document contains no text after cleaning.")

    return {
        **document,
        "text": cleaned_text,
        "character_count": len(cleaned_text),
        "word_count": len(cleaned_text.split())
    }

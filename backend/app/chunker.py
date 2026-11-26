
def chunk_text(
    text: str,
    chunk_size: int = 180,
    overlap: int = 30
) -> list:
    """
    Divide text into overlapping word-based chunks.
    """

    if not text or not text.strip():
        raise ValueError("Text cannot be empty.")

    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than zero.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("Overlap must be smaller than chunk size.")

    words = text.split()
    chunks = []

    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]

        chunks.append({
            "chunk_id": len(chunks),
            "text": " ".join(chunk_words),
            "start_word": start,
            "end_word": min(end, len(words))
        })

        if end >= len(words):
            break

        start = end - overlap

    return chunks


def chunk_document(document: dict) -> list:
    """
    Create chunks from a cleaned document.
    """

    if "text" not in document:
        raise ValueError("Document has no text.")

    chunks = chunk_text(document["text"])

    for chunk in chunks:
        chunk["source"] = document.get(
            "file_name", "unknown"
        )

    return chunks

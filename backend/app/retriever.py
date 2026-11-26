from app.vector_store import search_vectors


def retrieve_context(question: str, top_k: int = 4):
    return search_vectors(question, top_k=top_k)


def format_context(results: list[dict]) -> str:
    if not results:
        return ""

    sections = []

    for number, item in enumerate(results, start=1):
        source = item.get("source", "Unknown document")
        content = item.get("text", "")

        sections.append(
            f"[Source {number}: {source}]\n{content}"
        )

    return "\n\n".join(sections)

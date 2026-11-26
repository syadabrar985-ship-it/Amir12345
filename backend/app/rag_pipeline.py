from app.retriever import retrieve_context, format_context
from app.generator import generate_answer


def ask_question(question: str):
    results = retrieve_context(question)

    context = format_context(results)
    answer = generate_answer(question, context)

    sources = []

    for item in results:
        source = item.get("source", "Unknown document")

        if source not in sources:
            sources.append(source)

    return {
        "answer": answer,
        "sources": sources
    }

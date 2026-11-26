
from pathlib import Path

from app.extractor import extract_document
from app.cleaner import clean_document
from app.chunker import chunk_document
from app.embeddings import EmbeddingModel
from app.vector_store import FAISSVectorStore
from app.retriever import Retriever
from app.generator import generate_answer


BASE_DIR = Path(__file__).resolve().parents[1]

VECTOR_DB_PATH = BASE_DIR / "vector_db"


def index_pdf(pdf_path: str):
    """
    Process a PDF and save its knowledge in FAISS.
    """

    print("1. Extracting PDF text...")

    document = extract_document(pdf_path)

    print("2. Cleaning extracted text...")

    document = clean_document(document)

    print("3. Creating text chunks...")

    chunks = chunk_document(document)

    if not chunks:
        raise ValueError("No chunks were created.")

    print("4. Creating embeddings...")

    embedding_model = EmbeddingModel()

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = embedding_model.create_embeddings(texts)

    print("5. Saving FAISS index...")

    vector_store = FAISSVectorStore()

    vector_store.add_documents(chunks, embeddings)

    vector_store.save(str(VECTOR_DB_PATH))

    print("Knowledge base created successfully!")

    return {
        "file_name": document["file_name"],
        "total_chunks": len(chunks),
        "total_words": document["word_count"],
        "status": "success"
    }


def answer_question(question: str):
    """
    Retrieve relevant information and generate an answer.
    """

    print("1. Searching knowledge base...")

    retriever = Retriever()

    results = retriever.retrieve(
        query=question,
        top_k=4
    )

    context_parts = []
    sources = []

    for result in results:

        chunk = result["chunk"]

        context_parts.append(chunk["text"])

        source = chunk.get("source", "Unknown")

        if source not in sources:
            sources.append(source)

    context = "\n\n".join(context_parts)

    print("2. Generating answer with Groq...")

    answer = generate_answer(
        question=question,
        context=context
    )

    return {
        "question": question,
        "answer": answer,
        "sources": sources
    }

# AI Lead Generation Assistant Using RAG

A document-based AI assistant designed to help with lead generation
knowledge, client information, outreach processes, and related tasks.

## Main Features

- PDF, TXT, and Markdown document support
- Text extraction and cleaning
- Text chunking
- Sentence Transformers embeddings
- FAISS vector database
- Semantic document retrieval
- Groq LLM integration
- FastAPI backend
- HTML, CSS, and JavaScript frontend

## Project Structure

- backend/app: RAG and API code
- backend/data/source_documents: Original documents
- backend/data/processed: Processed data
- backend/vector_db: FAISS index and metadata
- frontend: Website interface
- tests: Test files

## Setup

Install the dependencies:

    pip install -r backend/requirements.txt

Create a `.env` file in the project root using `.env.example` as a template.

Add your Groq API key to `.env`.

## Start the Backend

From the backend directory, run:

    uvicorn app.main:app --reload

The API will run at:

    http://localhost:8000

API documentation:

    http://localhost:8000/docs

## Add Documents

Upload PDF, TXT, or Markdown files using:

    POST /documents/upload

Or place documents directly in:

    backend/data/source_documents/

## Build the Vector Database

Send a POST request to:

    http://localhost:8000/documents/index

This extracts documents, creates chunks and embeddings, and saves
the FAISS index.

## Ask Questions

Send a POST request to:

    http://localhost:8000/chat

Example request:

    {
        "question": "What services does Amir offer?"
    }

## Important

The assistant answers using the documents indexed in its knowledge base.
It does not automatically browse websites, contact prospects, verify
email addresses, or update CRM systems.

from pathlib import Path
from shutil import copyfileobj

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import SOURCE_DIR
from app.extractor import extract_text, SUPPORTED_EXTENSIONS
from app.cleaner import clean_text
from app.chunker import split_into_chunks
from app.vector_store import save_vector_store
from app.rag_pipeline import ask_question


app = FastAPI(
    title="AI Lead Generation Assistant",
    description="A document-based RAG assistant for Amir.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


class ChatRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {
        "message": "AI Lead Generation Assistant API is running."
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/chat")
def chat(request: ChatRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Please enter a question."
        )

    try:
        return ask_question(question)

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


@app.post("/documents/upload")
def upload_document(file: UploadFile = File(...)):
    filename = Path(file.filename or "").name
    extension = Path(filename).suffix.lower()

    if not filename or extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, TXT, and Markdown files are supported."
        )

    destination = SOURCE_DIR / filename

    try:
        with destination.open("wb") as output:
            copyfileobj(file.file, output)

        return {
            "message": "Document uploaded successfully.",
            "filename": filename
        }

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))

    finally:
        file.file.close()


@app.post("/documents/index")
def index_documents():
    all_chunks = []
    all_metadata = []
    processed_files = []

    for file_path in SOURCE_DIR.iterdir():
        if not file_path.is_file():
            continue

        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        try:
            raw_text = extract_text(str(file_path))
            cleaned_text = clean_text(raw_text)
            chunks = split_into_chunks(cleaned_text)

            for chunk_number, chunk in enumerate(chunks, start=1):
                all_chunks.append(chunk)

                all_metadata.append({
                    "source": file_path.name,
                    "chunk": chunk_number,
                    "text": chunk
                })

            processed_files.append({
                "filename": file_path.name,
                "chunks": len(chunks)
            })

        except Exception as error:
            raise HTTPException(
                status_code=500,
                detail=f"Could not process {file_path.name}: {error}"
            )

    if not all_chunks:
        raise HTTPException(
            status_code=400,
            detail="No readable documents found. Upload a PDF, TXT, or MD file first."
        )

    try:
        total_chunks = save_vector_store(
            all_chunks,
            all_metadata
        )

        return {
            "message": "Documents indexed successfully.",
            "files": processed_files,
            "total_chunks": total_chunks
        }

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/documents")
def list_documents():
    files = []

    for file_path in SOURCE_DIR.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            files.append(file_path.name)

    return {"documents": files}

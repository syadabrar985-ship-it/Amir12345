
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

from app.rag_pipeline import index_pdf, answer_question


BASE_DIR = Path(__file__).resolve().parents[1]

SOURCE_DIR = BASE_DIR / "data" / "source_documents"

SOURCE_DIR.mkdir(parents=True, exist_ok=True)


app = FastAPI(
    title="Amir AI Lead Generation Assistant",
    description="RAG-based AI assistant using Amir's documents.",
    version="1.0.0"
)


class ChatRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {
        "message": "Amir AI Lead Generation Assistant is running."
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a PDF document.
    """

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    filename = Path(file.filename).name

    if not filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename."
        )

    destination = SOURCE_DIR / filename

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    if not content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid PDF."
        )

    if len(content) > 15 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="PDF must be smaller than 15 MB."
        )

    destination.write_bytes(content)

    return {
        "message": "PDF uploaded successfully.",
        "file_name": filename
    }


@app.get("/documents")
def list_documents():
    """
    List uploaded PDF documents.
    """

    files = list(SOURCE_DIR.glob("*.pdf"))

    return {
        "total_documents": len(files),
        "documents": [file.name for file in files]
    }


@app.post("/documents/index")
def index_document(filename: str | None = None):
    """
    Extract, clean, chunk, embed and index a PDF.
    """

    pdf_files = sorted(SOURCE_DIR.glob("*.pdf"))

    if filename:
        safe_filename = Path(filename).name

        if safe_filename != filename:
            raise HTTPException(
                status_code=400,
                detail="Invalid filename."
            )

        pdf_path = SOURCE_DIR / safe_filename

        if not pdf_path.is_file() or pdf_path.suffix.lower() != ".pdf":
            raise HTTPException(
                status_code=404,
                detail="PDF document not found."
            )

    else:
        if not pdf_files:
            raise HTTPException(
                status_code=404,
                detail="No PDF documents found."
            )

        if len(pdf_files) > 1:
            raise HTTPException(
                status_code=400,
                detail="Multiple PDFs found. Provide a filename to index."
            )

        pdf_path = pdf_files[0]

    try:
        result = index_pdf(str(pdf_path))
        return result

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Indexing failed: {str(error)}"
        )


@app.post("/chat")
def chat(request: ChatRequest):
    """
    Ask a question using the indexed knowledge base.
    """

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    try:
        result = answer_question(request.question)
        return result

    except FileNotFoundError:
        raise HTTPException(
            status_code=400,
            detail="Knowledge base not found. Index a document first."
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Could not generate answer: {str(error)}"
        )


import os
import sys
import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Amir AI Assistant",
    page_icon="🤖",
    layout="wide"
)

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BACKEND_DIR.parent

sys.path.insert(0, str(BACKEND_DIR))

# Load secure Streamlit secrets before importing the RAG pipeline
try:
    for key in ["GROQ_API_KEY", "GROQ_MODEL"]:
        if key in st.secrets:
            os.environ[key] = str(st.secrets[key])
except Exception:
    pass

from app.rag_pipeline import index_pdf, answer_question

SOURCE_DIR = BACKEND_DIR / "data" / "source_documents"
VECTOR_DB_DIR = BACKEND_DIR / "vector_db"

SOURCE_DIR.mkdir(parents=True, exist_ok=True)

def knowledge_base_ready():
    return (
        (VECTOR_DB_DIR / "index.faiss").exists()
        and (VECTOR_DB_DIR / "chunks.json").exists()
    )

st.title("🤖 Amir AI Lead Generation Assistant")
st.caption(
    "Your document-based AI assistant powered by "
    "RAG, FAISS, Sentence Transformers and Groq."
)

with st.sidebar:
    st.header("Knowledge Base")

    existing_pdfs = list(SOURCE_DIR.glob("*.pdf"))

    if existing_pdfs:
        st.write("Existing documents:")
        for pdf in existing_pdfs:
            st.write(f"📄 {pdf.name}")

        if st.button("Index Existing Documents", use_container_width=True):
            try:
                with st.spinner("Building knowledge base..."):
                    for pdf in existing_pdfs:
                        index_pdf(str(pdf))

                st.success("Knowledge base created successfully!")
                st.rerun()

            except Exception as error:
                st.error(f"Indexing failed: {error}")
    else:
        st.info("No existing PDF documents found.")

    st.divider()

    st.subheader("Upload New PDF")

    uploaded_file = st.file_uploader(
        "Choose a PDF document",
        type=["pdf"]
    )

    if uploaded_file and st.button(
        "Upload and Index PDF",
        use_container_width=True
    ):
        pdf_path = SOURCE_DIR / Path(uploaded_file.name).name

        try:
            pdf_path.write_bytes(uploaded_file.getvalue())

            with st.spinner("Processing your document..."):
                index_pdf(str(pdf_path))

            st.success("Document indexed successfully!")
            st.rerun()

        except Exception as error:
            st.error(f"Upload failed: {error}")

    st.divider()

    st.subheader("System Status")

    if knowledge_base_ready():
        st.success("Knowledge base is ready")
    else:
        st.warning("Knowledge base is not indexed yet")

st.subheader("Chat with Amir's AI Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input(
    "Ask about Amir's lead generation business..."
)

if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        if not knowledge_base_ready():
            answer = (
                "The knowledge base is not ready yet. "
                "Please index the existing PDF first."
            )
            st.warning(answer)
        else:
            with st.spinner("Searching the knowledge base..."):
                try:
                    result = answer_question(question)
                    answer = result["answer"]

                    st.markdown(answer)

                    if result.get("sources"):
                        with st.expander("View Sources"):
                            for source in result["sources"]:
                                st.write(f"📄 {source}")

                except Exception as error:
                    answer = f"Unable to generate an answer: {error}"
                    st.error(answer)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

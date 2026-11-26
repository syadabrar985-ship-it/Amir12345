
import streamlit as st
import sys
from pathlib import Path

# Add project root to Python path
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BACKEND_DIR.parent

sys.path.insert(0, str(BACKEND_DIR))

import os

if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

if "GROQ_MODEL" in st.secrets:
    os.environ["GROQ_MODEL"] = st.secrets["GROQ_MODEL"]

from app.rag_pipeline import index_pdf, answer_question


SOURCE_DIR = BACKEND_DIR / "data" / "source_documents"

SOURCE_DIR.mkdir(parents=True, exist_ok=True)


# Page configuration
st.set_page_config(
    page_title="Amir AI Assistant",
    page_icon="🤖",
    layout="wide"
)


# Application title
st.title("🤖 Amir AI Lead Generation Assistant")

st.caption(
    "An AI assistant powered by RAG, FAISS, "
    "Sentence Transformers and Groq."
)


# Sidebar
with st.sidebar:

    st.header("Knowledge Base")

    st.write("Upload Amir's documents to update the knowledge base.")

    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"]
    )

    if uploaded_file:

        if st.button("Upload and Index PDF"):

            pdf_path = SOURCE_DIR / Path(uploaded_file.name).name

            try:
                pdf_path.write_bytes(uploaded_file.getvalue())

                with st.spinner("Processing document..."):

                    result = index_pdf(str(pdf_path))

                st.success("Document indexed successfully!")

                st.json(result)

                st.session_state["knowledge_ready"] = True

            except Exception as error:

                st.error(f"Indexing failed: {error}")

    st.divider()

    st.subheader("System Status")

    if st.session_state.get("knowledge_ready", False):
        st.success("Knowledge base indexed")
    else:
        st.info("Upload and index a document to begin")


# Chat interface
st.subheader("Chat with Amir's AI Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []


# Display previous messages
for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# User input
question = st.chat_input(
    "Ask something about Amir's lead generation business..."
)


if question:

    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):

        with st.spinner("Searching knowledge base..."):

            try:

                result = answer_question(question)

                answer = result["answer"]

                st.markdown(answer)

                if result.get("sources"):

                    with st.expander("Sources"):
                        for source in result["sources"]:
                            st.write(f"📄 {source}")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as error:

                st.error(
                    f"Unable to answer your question: {error}"
                )

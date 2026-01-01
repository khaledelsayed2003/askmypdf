from typing import Dict, Any
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


def index_pdf_to_chroma(pdf_path: str, pdf_id: str, chroma_dir: str) -> None:
   
    # load PDF pages
    loader = PyMuPDFLoader(pdf_path)
    docs = loader.load()  # one Document per page

    # split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,
        chunk_overlap=150,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = splitter.split_documents(docs)

    # Temporary debug prints (remove later)
    print(f"[INDEX] Pages loaded: {len(docs)}")
    print(f"[INDEX] Chunks created: {len(chunks)}")

    # We'll store chunks in Chroma later
    return


def answer_question(question: str, pdf_id: str, chroma_dir: str) -> Dict[str, Any]:
    raise NotImplementedError("Answering is not implemented yet.")

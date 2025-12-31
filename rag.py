from typing import Dict, Any
from langchain_community.document_loaders import PyMuPDFLoader


def index_pdf_to_chroma(pdf_path: str, pdf_id: str, chroma_dir: str) -> None:
    
    # Load PDF pages as LangChain Documents.
    loader = PyMuPDFLoader(pdf_path)
    docs = loader.load()  # one Document per page

    # Temporary debug output (we will remove later)
    print(f"[INDEX] Loaded {len(docs)} pages from PDF: {pdf_path}")

    return


def answer_question(question: str, pdf_id: str, chroma_dir: str) -> Dict[str, Any]:
   
    raise NotImplementedError("Answering is not implemented yet")
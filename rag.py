from typing import Dict, Any
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings


def _get_embeddings() -> HuggingFaceEmbeddings:
    """
    Local embeddings (FREE).
    Converts text into vectors using sentence-transformers.
    """
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


def index_pdf_to_chroma(pdf_path: str, pdf_id: str, chroma_dir: str) -> None:
    # load PDF pages(extract text from pdf)
    loader = PyMuPDFLoader(pdf_path)
    docs = loader.load()

    # split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,
        chunk_overlap=150,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = splitter.split_documents(docs)

    # create embeddings object (we'll use it for storage later)
    embeddings = _get_embeddings()

    # Temporary debug print (we will remove it later)
    sample_vec = embeddings.embed_query("hello world")
    print(f"[EMBED] Sample embedding vector length: {len(sample_vec)}")
    print(f"[INDEX] Pages loaded: {len(docs)} | Chunks created: {len(chunks)}")

    return


def answer_question(question: str, pdf_id: str, chroma_dir: str) -> Dict[str, Any]:
    raise NotImplementedError("Answering is not implemented yet.")

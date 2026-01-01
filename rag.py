from typing import Dict, Any
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma


def _get_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


def _collection_name(pdf_id: str) -> str:
    """
    create a safe collection name for Chroma.
    We remove '-' because some setups prefer simple names.
    """
    return f"pdf_{pdf_id}".replace("-", "")


def index_pdf_to_chroma(pdf_path: str, pdf_id: str, chroma_dir: str) -> None:
    # load PDF pages (extract text from pdf)
    loader = PyMuPDFLoader(pdf_path)
    docs = loader.load()

    # split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,
        chunk_overlap=150,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = splitter.split_documents(docs)

    # embeddings
    embeddings = _get_embeddings()

    # initialize a persistent Chroma collection (empty for now)
    collection = _collection_name(pdf_id)

    db = Chroma(
        collection_name=collection,
        embedding_function=embeddings,
        persist_directory=chroma_dir,
    )

    # Temporary debug prints
    print(f"[INDEX] Collection ready: {collection}")
    print(f"[INDEX] Pages loaded: {len(docs)} | Chunks created: {len(chunks)}")

    return


def answer_question(question: str, pdf_id: str, chroma_dir: str) -> Dict[str, Any]:
    raise NotImplementedError("Answering is not implemented yet.")
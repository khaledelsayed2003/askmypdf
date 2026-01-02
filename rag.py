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
    return f"pdf_{pdf_id}".replace("-", "")


def index_pdf_to_chroma(pdf_path: str, pdf_id: str, chroma_dir: str) -> None:
    loader = PyMuPDFLoader(pdf_path)
    docs = loader.load()  # one Document per page with metadata (page number)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,
        chunk_overlap=150,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = splitter.split_documents(docs)

    # ensure metadata is present and consistent
    for i, d in enumerate(chunks):
        d.metadata["pdf_id"] = pdf_id
        d.metadata["chunk_id"] = i

        # PyMuPDFLoader usually provides "page" already.
        # But we enforce it safely in case it's missing.
        if "page" not in d.metadata:
            d.metadata["page"] = 0  # fallback

    embeddings = _get_embeddings()

    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=_collection_name(pdf_id),
        persist_directory=chroma_dir,
    )

    # Debug: show a sample chunk metadata (we will remove later)
    sample_meta = chunks[0].metadata if chunks else {}
    print(f"[INDEX] Stored {len(chunks)} chunks in: {_collection_name(pdf_id)}")
    print(f"[INDEX] Sample metadata: {sample_meta}")


def answer_question(question: str, pdf_id: str, chroma_dir: str) -> Dict[str, Any]:
    raise NotImplementedError("Answering is not implemented yet.")

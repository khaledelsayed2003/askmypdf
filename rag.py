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

    # attach helpful metadata to each chunk
    for i, d in enumerate(chunks):
        d.metadata["pdf_id"] = pdf_id
        d.metadata["chunk_id"] = i

    embeddings = _get_embeddings()

    # save chunks into Chroma (persist to disk)
    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=_collection_name(pdf_id),
        persist_directory=chroma_dir,
    )

    print(f"[INDEX] Stored {len(chunks)} chunks in Chroma collection: {_collection_name(pdf_id)}")


def answer_question(question: str, pdf_id: str, chroma_dir: str) -> Dict[str, Any]:
    raise NotImplementedError("Answering is not implemented yet.")
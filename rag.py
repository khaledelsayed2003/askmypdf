from typing import Dict, Any, List, Tuple
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
    """
    - Convert question to embedding
    - Retrieve top matching chunks from Chroma
    - Return raw retrieved text (no LLM yet)
    """

    embeddings = _get_embeddings()

    # Load existing Chroma collection for this PDF
    db = Chroma(
        collection_name=_collection_name(pdf_id),
        embedding_function=embeddings,
        persist_directory=chroma_dir,
    )

    # Search for similar chunks
    results: List[Tuple[Any, float]] = db.similarity_search_with_score(
        question,
        k=5
    )

    if not results:
        return {
            "answer": "No relevant content found.",
            "source": ""
        }

    # Collect retrieved chunks
    retrieved_chunks = []
    pages = set()

    for doc, score in results:
        retrieved_chunks.append(doc.page_content)

        page = doc.metadata.get("page")
        if page is not None:
            pages.add(page + 1)  # human-readable page number

    combined_text = "\n\n---\n\n".join(retrieved_chunks)
    pages_str = ", ".join(str(p) for p in sorted(pages))

    # TEMPORARY response (for testing retrieval)
    return {
        "answer": combined_text,
        "source": f"Source pages: {pages_str}"
    }


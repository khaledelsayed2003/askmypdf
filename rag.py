from typing import Dict, Any, List, Tuple
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate


def _get_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


# temperature=0 means more deterministic, less hallucination.
def _get_llm() -> ChatOllama:
    return ChatOllama(model="gemma3:4b", temperature=0)


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



NOT_FOUND_TEXT = "Answer is not in this PDF."


def answer_question(question: str, pdf_id: str, chroma_dir: str) -> Dict[str, Any]:
    embeddings = _get_embeddings()

    db = Chroma(
        collection_name=_collection_name(pdf_id),
        embedding_function=embeddings,
        persist_directory=chroma_dir,
    )

    # retrieve top chunks.
    results: List[Tuple[Any, float]] = db.similarity_search_with_score(question, k=6)

    if not results:
        return {"answer": NOT_FOUND_TEXT, "source": ""}

    context_parts = []
    pages = set()

    for doc, score in results:
        context_parts.append(doc.page_content)

        page = doc.metadata.get("page")
        if page is not None:
            pages.add(int(page) + 1)

    context = "\n\n---\n\n".join(context_parts)
    pages_str = ", ".join(str(p) for p in sorted(pages)) if pages else ""

    llm = _get_llm()

    # verification prompt: YES/NO only
    verify_prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Answer with ONLY one word: YES or NO.\n"
         "Say YES only if the CONTEXT clearly contains the answer.\n"
         "Otherwise say NO.\n"),
        ("user",
         "QUESTION:\n{question}\n\nCONTEXT:\n{context}\n")
    ])

    verify_msg = verify_prompt.format_messages(question=question, context=context)
    verify_resp = (llm.invoke(verify_msg).content or "").strip().upper()

    if not verify_resp.startswith("YES"):
        return {"answer": NOT_FOUND_TEXT, "source": ""}

    # answer prompt (only if verified)
    answer_prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a PDF-only assistant.\n"
         "Rules:\n"
         "1) Answer ONLY using the CONTEXT from the PDF.\n"
         "2) If the answer is not explicitly in the CONTEXT, reply exactly:\n"
         f"   {NOT_FOUND_TEXT}\n"
         "3) Do not use outside knowledge.\n"
         "4) Keep the answer short and clear.\n"),
        ("user",
         "QUESTION:\n{question}\n\nCONTEXT:\n{context}\n")
    ])

    answer_msg = answer_prompt.format_messages(question=question, context=context)
    answer_text = (llm.invoke(answer_msg).content or "").strip()

    if not answer_text:
        answer_text = NOT_FOUND_TEXT

    source = f"Source pages: {pages_str}" if pages_str else ""
    return {"answer": answer_text, "source": source}
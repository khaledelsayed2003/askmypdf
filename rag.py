from typing import Dict, Any


def index_pdf_to_chroma(pdf_path: str, pdf_id: str, chroma_dir: str) -> None:
    """
    Takes a PDF file path and builds a searchable index (vector store)
    that will be stored inside chroma_dir under a collection name derived from pdf_id.
    """
    # later we will implement: load PDF -> split text -> embed -> store in Chroma
    raise NotImplementedError("Indexing is not implemented yet.")


def answer_question(question: str, pdf_id: str, chroma_dir: str) -> Dict[str, Any]:
    """
    Takes a user question and returns:
      {
        "answer": "...",
        "source": "Source pages: ..."
      }
    """
    # later we will implement: retrieve chunks -> build context -> ask LLM -> return answer
    raise NotImplementedError("Answering is not implemented yet.")
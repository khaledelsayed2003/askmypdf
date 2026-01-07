from rag import index_pdf_to_chroma, answer_question
import os
import uuid
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv


# Load environment variables from config/.env
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ENV_PATH = os.path.join(BASE_DIR, "config", ".env")
load_dotenv(ENV_PATH)

app = Flask(__name__)

# Secret key for cookie/session security
app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "dev-secret-change-me"
)

# Folders
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
CHROMA_DIR = os.path.join(BASE_DIR, "chroma_store")

# Create folders at startup
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CHROMA_DIR, exist_ok=True)


@app.get("/")
@app.get("/home")
def home():
    pdf_id = session.get("pdf_id")
    pdf_name = session.get("pdf_name", "")
    pdf_ready = bool(pdf_id)

    return render_template(
        "index.html",
        pdf_ready=pdf_ready,
        pdf_name=pdf_name
    )


@app.post("/upload")
def upload_pdf():
    if "pdf" not in request.files:
        return jsonify({"ok": False, "error": "No file field named 'pdf'."}), 400

    file = request.files["pdf"]

    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"ok": False, "error": "Only PDF files are allowed."}), 400

    # Ensure folders exist at request time too (Windows/OneDrive safe)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(CHROMA_DIR, exist_ok=True)

    pdf_id = str(uuid.uuid4())
    filename = f"{pdf_id}.pdf"
    save_path = os.path.join(UPLOAD_DIR, filename)

    file.save(save_path)
    
    # Index into Chroma.
    try:
        index_pdf_to_chroma(
            pdf_path=save_path,
            pdf_id=pdf_id,
            chroma_dir=CHROMA_DIR
        )
    except Exception as e:
        return jsonify({"ok": False, "error": f"Indexing failed: {e}"}), 500


    # Store PDF info in session
    session["pdf_id"] = pdf_id
    session["pdf_name"] = file.filename

    return jsonify({
        "ok": True,
        "pdf_id": pdf_id,
        "pdf_name": file.filename,
        "message": "PDF uploaded successfully."
    })


@app.post("/ask")
def ask():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()

    pdf_id = session.get("pdf_id")
    if not pdf_id:
        return jsonify({"ok": False, "error": "Upload a PDF first."}), 400

    if not question:
        return jsonify({"ok": False, "error": "Type a question."}), 400
    
    try:
        result = answer_question(
            question=question,
            pdf_id=pdf_id,
            chroma_dir=CHROMA_DIR
        )
    except Exception as e:
        return jsonify({"ok": False, "error": f"Answering failed: {e}"}), 500

    return jsonify({
        "ok": True,
        "answer": result["answer"],
        "source": result.get("source", "")
    })


@app.post("/reset")
def reset():
    session.pop("pdf_id", None)
    session.pop("pdf_name", None)
    return jsonify({"ok": True})



if __name__ == "__main__":
    app.run(debug=True)

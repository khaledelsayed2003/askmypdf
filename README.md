# 📄 AskMyPDF

**AskMyPDF** is a Flask-based **PDF Question Answering (RAG) web application** that allows users to upload a PDF and ask questions about its content.
The system answers **only from the uploaded PDF**, using semantic search and a local LLM, with clear source page references.

---

## 🚀 Features

- 📤 Upload a PDF file
- 🧠 Semantic search over PDF content (vector embeddings)
- 💬 Chat-style interface (Instagram / WhatsApp style)
- 📚 Answers strictly grounded in the PDF (no hallucination)
- 📄 Source page references for each answer
- 🔄 Reset session (PDF + chat)
- ⚡ No page reloads (AJAX / Fetch API)
- 🔐 Session-based chat memory
- 🧠 Local LLM inference (no OpenAI key required)

---

## 🏗️ Architecture Overview

This project follows a **Retrieval-Augmented Generation (RAG)** architecture:

```
PDF → Text Extraction → Chunking → Embeddings → Vector DB (Chroma)
                                  ↓
User Question → Semantic Search → Relevant Chunks → LLM → Answer
```

### Tech Stack

| Layer           | Technology                     |
| --------------- | ------------------------------ |
| Backend         | Flask (Python)                 |
| Frontend        | HTML, CSS, JavaScript          |
| Templating      | Jinja2                         |
| Vector DB       | ChromaDB                       |
| Embeddings      | Sentence-Transformers (MiniLM) |
| LLM             | Ollama (Gemma 3)               |
| PDF Parsing     | PyMuPDF                        |
| Session Storage | Flask Sessions                 |

---

## 📂 Project Structure

```
askmypdf/
├── app.py                # Flask application
├── rag.py                # RAG pipeline (index + retrieval + LLM)
├── uploads/              # Uploaded PDF files
├── chroma_store/         # Persistent vector database
├── templates/
│   ├── base.html
│   └── index.html
├── static/
│   ├── style.css
│   └── app.js
├── config/
│   └── .env
├── .gitignore
├── LICENSE
├── requirements.txt
└── README.md
```

---

## 🧠 How It Works (Step by Step)

1. User uploads a PDF
2. PDF text is extracted using **PyMuPDF**
3. Text is split into overlapping chunks
4. Each chunk is converted into a vector embedding
5. Vectors are stored in **ChromaDB**
6. User asks a question
7. Most relevant chunks are retrieved using semantic similarity
8. LLM verifies if the answer exists in the PDF
9. LLM generates a final answer **only from the PDF**
10. Source page numbers are returned

---

## 🛡️ Anti-Hallucination Strategy

- LLM is **not allowed** to use outside knowledge
- A verification step checks whether the answer exists in the retrieved text
- If not found, the system replies:

```
Answer is not in this PDF.
```

---

## 🖥️ User Interface

- Chat bubbles (user → right, assistant → left)
- Smooth scrolling chat
- Fixed bottom input bar
- 🎤 Voice input (speech-to-text)
- Status messages (uploading, thinking, done)
- PDF name badge in navbar
- Reset button clears PDF + chat without reload

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository

```bash
git clone https://github.com/khaledelsayed2003/askmypdf.git
cd askmypdf
```

### 2️⃣ Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate    # macOS / Linux
venv\Scripts\activate       # Windows
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Install Ollama

Download from:
👉 [https://ollama.com](https://ollama.com)

Pull the model:

```bash
ollama pull gemma3:4b
```

### 5️⃣ Environment variables

Create `config/.env`:

```env
FLASK_SECRET_KEY=your-secret-key
```

### 6️⃣ Run the app

```bash
python app.py
```

Open in browser:

```
http://127.0.0.1:5000
```

---

## 🧪 Example Usage

1. Upload a PDF (CV, paper, report, book)
2. Ask:

   - _“What programming languages are listed?”_
   - _“What is the project objective?”_
   - _“Who is the author?”_

3. Get:

   - A concise answer
   - Exact source page(s)

---

## 🔄 Reset Behavior

- Clears:

  - Uploaded PDF
  - Vector collection
  - Chat history

- UI resets instantly (no reload)

---

## 🧾 Limitations

- Works with **text-based PDFs** (not scanned images)
- Large PDFs may take longer to index
- Requires local LLM (Ollama) to be running

---

## 🛠️ Future Improvements

- 📑 Multi-PDF support
- 🔍 Highlight answer text inside PDF
- 📊 Confidence scoring
- 🌐 Deployment (Docker / Cloud)

---

## 📜 License

This project is licensed under the **MIT License**.
You are free to use, modify, and distribute it.

---

## 👤 Author

**Khaled Elsayed**

- 📧 Email: khaled.elsayed2206@gmail.com
- 🧠 Built for learning, research, and real-world RAG systems

---

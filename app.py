import os
import uuid
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Base directory of the project
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Folder where uploaded PDFs will be stored
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

# Create uploads folder if it does not exist
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
@app.get("/home")
def home():
    return render_template("index.html")


@app.post("/upload")
def upload_pdf():
    # Check if file field exists
    if "pdf" not in request.files:
        return jsonify({
            "ok": False,
            "error": "No file field named 'pdf'."
        }), 400

    file = request.files["pdf"]

    #Check file extension
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({
            "ok": False,
            "error": "Only PDF files are allowed."
        }), 400

    # Generate unique filename
    pdf_id = str(uuid.uuid4())
    filename = f"{pdf_id}.pdf"
    
    # Save the file inside uploads folder 
    save_path = os.path.join(UPLOAD_DIR, filename)
    file.save(save_path)

    # Return success response
    return jsonify({
        "ok": True,
        "pdf_id": pdf_id,
        "message": "PDF uploaded successfully."
    })
    

if __name__ == "__main__":
    app.run(debug=True)

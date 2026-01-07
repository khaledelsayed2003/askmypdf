const pdfFile = document.getElementById("pdfFile");
const uploadBtn = document.getElementById("uploadBtn");
const questionInput = document.getElementById("questionInput");
const sendBtn = document.getElementById("sendBtn");
const statusLine = document.getElementById("statusLine");

//(answer output)
const answerBox = document.getElementById("answerBox");
const answerText = document.getElementById("answerText");
const answerSource = document.getElementById("answerSource");

function setStatus(msg) {
  statusLine.textContent = msg || "";
}

// Upload button -> open file picker
uploadBtn.addEventListener("click", () => pdfFile.click());

// When user selects a PDF
pdfFile.addEventListener("change", async () => {
  if (!pdfFile.files.length) return;

  const file = pdfFile.files[0];
  setStatus("Uploading and indexing PDF...");

  // Disable inputs while uploading
  uploadBtn.disabled = true;
  questionInput.disabled = true;
  sendBtn.disabled = true;

  const formData = new FormData();
  formData.append("pdf", file);

  try {
    const res = await fetch("/upload", { method: "POST", body: formData });
    const data = await res.json();

    if (!data.ok) {
      setStatus("Upload failed: " + data.error);
      uploadBtn.disabled = false;
      return;
    }

    //Enable asking now
    setStatus(`PDF ready: ${data.pdf_name}. You can now ask questions.`);
    questionInput.disabled = false;
    sendBtn.disabled = false;
    uploadBtn.disabled = false;

    //clear previous answer
    if (answerBox) answerBox.classList.add("d-none");

    // (No reload for now — we want to test /ask directly)
  } catch (err) {
    setStatus("Upload error. Please try again.");
    uploadBtn.disabled = false;
  }
});

// Send question to /ask
async function askQuestion() {
  const q = (questionInput.value || "").trim();
  if (!q) return;

  setStatus("Thinking...");
  sendBtn.disabled = true;

  try {
    const res = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: q }),
    });

    const data = await res.json();
    sendBtn.disabled = false;

    if (!data.ok) {
      setStatus(data.error);
      return;
    }

    setStatus("Done.");

    // Show answer in the answer box
    if (answerBox) answerBox.classList.remove("d-none");
    if (answerText) answerText.textContent = data.answer || "";
    if (answerSource) answerSource.textContent = data.source || "";

  } catch (err) {
    sendBtn.disabled = false;
    setStatus("Ask error. Please try again.");
  }
}

sendBtn.addEventListener("click", askQuestion);

questionInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") askQuestion();
});

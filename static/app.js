const pdfFile = document.getElementById("pdfFile");
const uploadBtn = document.getElementById("uploadBtn");
const questionInput = document.getElementById("questionInput");
const sendBtn = document.getElementById("sendBtn");
const statusLine = document.getElementById("statusLine");
const micBtn = document.getElementById("micBtn");

// Chat UI container (from index.html)
const chatArea = document.getElementById("chatArea");

// Navbar elements (from base.html)
const pdfBadge = document.getElementById("pdfBadge");
const resetBtn = document.getElementById("resetBtn");

function setStatus(msg) {
  if (!statusLine) return;
  statusLine.textContent = msg || "";
}

function setPdfBadgeReady(pdfName) {
  if (!pdfBadge) return;
  pdfBadge.textContent = `PDF: ${pdfName}`;
  pdfBadge.classList.remove("text-bg-warning");
  pdfBadge.classList.add("text-bg-light");
}

function setPdfBadgeEmpty() {
  if (!pdfBadge) return;
  pdfBadge.textContent = "No PDF uploaded";
  pdfBadge.classList.remove("text-bg-light");
  pdfBadge.classList.add("text-bg-warning");
}

// ---------- Chat helpers (no reload) ----------
function scrollChatToBottom() {
  if (!chatArea) return;
  chatArea.scrollTop = chatArea.scrollHeight;
}

function addUserMessage(text) {
  if (!chatArea) return;

  const row = document.createElement("div");
  row.className = "msg-row user";

  const bubble = document.createElement("div");
  bubble.className = "msg-bubble user-bubble";
  bubble.textContent = text;

  row.appendChild(bubble);
  chatArea.appendChild(row);
  scrollChatToBottom();
}

function addAssistantMessage(text, source) {
  if (!chatArea) return;

  const row = document.createElement("div");
  row.className = "msg-row assistant";

  const bubble = document.createElement("div");
  bubble.className = "msg-bubble assistant-bubble";

  const answerDiv = document.createElement("div");
  answerDiv.className = "answer-text";
  answerDiv.textContent = text || "";

  bubble.appendChild(answerDiv);

  if (source) {
    const sourceDiv = document.createElement("div");
    sourceDiv.className = "source-text";
    sourceDiv.textContent = source;
    bubble.appendChild(sourceDiv);
  }

  row.appendChild(bubble);
  chatArea.appendChild(row);
  scrollChatToBottom();
}

function renderEmptyState() {
  if (!chatArea) return;
  chatArea.innerHTML = `
    <div class="empty-state">
      <h5 class="mb-2">Upload a PDF, then ask your question.</h5>
      <div class="text-muted">The system will answer only from the uploaded PDF.</div>
    </div>
  `;
  scrollChatToBottom();
}

// Upload button -> open file picker
uploadBtn?.addEventListener("click", () => pdfFile?.click());

// When user selects a PDF
pdfFile?.addEventListener("change", async () => {
  if (!pdfFile.files.length) return;

  const file = pdfFile.files[0];
  setStatus("Uploading and indexing PDF...");

  // Disable inputs while uploading
  if (uploadBtn) uploadBtn.disabled = true;
  if (questionInput) questionInput.disabled = true;
  if (sendBtn) sendBtn.disabled = true;

  const formData = new FormData();
  formData.append("pdf", file);

  try {
    const res = await fetch("/upload", { method: "POST", body: formData });
    const data = await res.json();

    if (!data.ok) {
      setStatus("Upload failed: " + data.error);
      if (uploadBtn) uploadBtn.disabled = false;
      return;
    }

    // Update navbar badge (no reload)
    setPdfBadgeReady(data.pdf_name);

    // Clear old chat UI (because new PDF = new chat)
    renderEmptyState();

    // Enable asking
    setStatus(`PDF ready: ${data.pdf_name}. You can now ask questions.`);
    if (questionInput) questionInput.disabled = false;
    if (sendBtn) sendBtn.disabled = false;
    if (uploadBtn) uploadBtn.disabled = false;
    if (micBtn) micBtn.disabled = false;


    // focus input
    questionInput?.focus();
  } catch (err) {
    setStatus("Upload error. Please try again.");
    if (uploadBtn) uploadBtn.disabled = false;
  }
});

// Send question to /ask
async function askQuestion() {
  const q = (questionInput?.value || "").trim();
  if (!q) return;

  // Remove empty-state if it exists
  const emptyState = chatArea?.querySelector(".empty-state");
  if (emptyState) emptyState.remove();

  // Show user message immediately
  addUserMessage(q);

  // Clear input
  if (questionInput) questionInput.value = "";

  setStatus("Thinking...");
  if (sendBtn) sendBtn.disabled = true;

  try {
    const res = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: q }),
    });

    const data = await res.json();
    if (sendBtn) sendBtn.disabled = false;

    if (!data.ok) {
      setStatus(data.error || "Error.");
      addAssistantMessage(data.error || "Error.", "");
      return;
    }

    setStatus("Done.");
    addAssistantMessage(data.answer || "", data.source || "");
  } catch (err) {
    if (sendBtn) sendBtn.disabled = false;
    setStatus("Ask error. Please try again.");
    addAssistantMessage("Ask error. Please try again.", "");
  }
}

sendBtn?.addEventListener("click", askQuestion);

questionInput?.addEventListener("keydown", (e) => {
  if (e.key === "Enter") askQuestion();
});

// Reset button: clear session + UI (no reload)
resetBtn?.addEventListener("click", async () => {
  try {
    const res = await fetch("/reset", { method: "POST" });
    const data = await res.json();

    if (!data.ok) {
      setStatus("Reset failed.");
      return;
    }

    // Update navbar badge
    setPdfBadgeEmpty();

    // Clear chat UI
    renderEmptyState();

    // Disable asking until new PDF uploaded
    if (questionInput) {
      questionInput.value = "";
      questionInput.disabled = true;
    }
    if (sendBtn) sendBtn.disabled = true;
    if (micBtn) micBtn.disabled = true;

    setStatus("Reset complete. Upload a new PDF.");
    if (uploadBtn) uploadBtn.disabled = false;
  } catch (err) {
    setStatus("Reset error. Please try again.");
  }
});


// ---------- Voice input----------
let recognition = null;

const SpeechRecognition =
  window.SpeechRecognition || window.webkitSpeechRecognition;

if (SpeechRecognition) {
  recognition = new SpeechRecognition();
  recognition.lang = "en-US";
  recognition.continuous = false;
  recognition.interimResults = false;

  recognition.onresult = (event) => {
    const text = event.results[0][0].transcript || "";
    if (questionInput) questionInput.value = text;
    setStatus("Voice captured. You can edit then press Send.");
  };

  recognition.onerror = () => {
    setStatus("Mic error. Try again.");
  };

  recognition.onend = () => {
    if (micBtn) micBtn.disabled = false;
  };
} else {
  if (micBtn) {
    micBtn.disabled = true;
    micBtn.title = "Voice not supported in this browser";
  }
}

micBtn?.addEventListener("click", () => {
  if (!recognition) return;

  if (micBtn) micBtn.disabled = true;
  setStatus("Listening...");
  recognition.start();
});


scrollChatToBottom();

const pdfFile = document.getElementById("pdfFile");
const uploadBtn = document.getElementById("uploadBtn");
const questionInput = document.getElementById("questionInput");
const sendBtn = document.getElementById("sendBtn");
const statusLine = document.getElementById("statusLine");

function setStatus(msg) {
  statusLine.textContent = msg || "";
}

// when user clicks Upload PDF
uploadBtn.addEventListener("click", () => {
  pdfFile.click();
});

// when user selects a file
pdfFile.addEventListener("change", async () => {
  if (!pdfFile.files.length) return;

  const file = pdfFile.files[0];
  setStatus("Uploading PDF...");

  const formData = new FormData();
  formData.append("pdf", file);

  try {
    const res = await fetch("/upload", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();

    if (!data.ok) {
      setStatus("Upload failed: " + data.error);
      return;
    }

    setStatus(`PDF ready: ${data.pdf_name}. You can now ask questions.`);
    window.location.reload();

  } catch (err) {
    setStatus("Upload error. Please try again.");
  }
});
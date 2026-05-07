let selectedFile = null;

const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("fileInput");
const analyzeBtn = document.getElementById("analyzeBtn");
const resultEl = document.getElementById("result");
const previewEl = document.getElementById("preview");
const marketplaceEl = document.getElementById("marketplace");
const sourceUrlEl = document.getElementById("sourceUrl");

function setFile(file) {
  selectedFile = file;
  dropzone.textContent = `Выбрано: ${file.name} (${Math.round(file.size / 1024)} KB)`;
}

fileInput.addEventListener("change", (e) => {
  if (e.target.files && e.target.files.length > 0) {
    setFile(e.target.files[0]);
  }
});

dropzone.addEventListener("click", () => dropzone.focus());
dropzone.setAttribute("tabindex", "0");

dropzone.addEventListener("paste", (event) => {
  const items = event.clipboardData?.items || [];
  for (const item of items) {
    if (item.type.startsWith("image/")) {
      const file = item.getAsFile();
      if (file) {
        setFile(file);
        event.preventDefault();
        return;
      }
    }
  }
});

analyzeBtn.addEventListener("click", async () => {
  if (!selectedFile) {
    alert("Сначала вставьте или выберите изображение.");
    return;
  }

  resultEl.textContent = "Обработка...";

  const formData = new FormData();
  formData.append("image", selectedFile);
  formData.append("marketplace", marketplaceEl.value);
  formData.append("source_url", sourceUrlEl.value.trim());

  try {
    const res = await fetch("/api/analyze", {
      method: "POST",
      body: formData,
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || "API error");
    }
    previewEl.src = data.normalized.preview_data_url;
    resultEl.textContent = JSON.stringify(data, null, 2);
  } catch (error) {
    resultEl.textContent = JSON.stringify({ ok: false, error: String(error) }, null, 2);
  }
});

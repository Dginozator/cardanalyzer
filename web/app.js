let selectedFile = null;
let isProcessing = false;

const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("fileInput");
const analyzeBtn = document.getElementById("analyzeBtn");
const resultEl = document.getElementById("result");
const previewEl = document.getElementById("preview");
const marketplaceEl = document.getElementById("marketplace");
const sourceUrlEl = document.getElementById("sourceUrl");
const copySpecBtn = document.getElementById("copySpecBtn");
const copyStatusEl = document.getElementById("copyStatus");

function setFile(file, autoAnalyze = false) {
  selectedFile = file;
  dropzone.textContent = `Выбрано: ${file.name} (${Math.round(file.size / 1024)} KB)`;
  if (autoAnalyze) {
    analyzeSelectedFile();
  }
}

fileInput.addEventListener("change", (e) => {
  if (e.target.files && e.target.files.length > 0) {
    setFile(e.target.files[0], true);
  }
});

dropzone.addEventListener("click", () => dropzone.focus());
dropzone.setAttribute("tabindex", "0");

function handleImagePaste(event) {
  const items = event.clipboardData?.items || [];
  for (const item of items) {
    if (item.type.startsWith("image/")) {
      const file = item.getAsFile();
      if (file) {
        setFile(file, true);
        event.preventDefault();
        return;
      }
    }
  }
}

dropzone.addEventListener("paste", handleImagePaste);
document.addEventListener("paste", handleImagePaste);

async function copySpecToClipboard() {
  const payload = resultEl.textContent.trim();
  if (!payload || payload === "{}" || payload === "Обработка...") {
    copyStatusEl.textContent = "Пока нечего копировать.";
    return;
  }
  try {
    await navigator.clipboard.writeText(payload);
    copyStatusEl.textContent = "Схема скопирована в буфер обмена.";
  } catch (_error) {
    copyStatusEl.textContent = "Не удалось скопировать. Проверьте доступ к буферу.";
  }
}

copySpecBtn.addEventListener("click", copySpecToClipboard);

async function analyzeSelectedFile() {
  if (isProcessing) {
    return;
  }
  if (!selectedFile) {
    alert("Сначала вставьте или выберите изображение.");
    return;
  }

  isProcessing = true;
  analyzeBtn.disabled = true;
  analyzeBtn.textContent = "Обработка...";
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
    resultEl.textContent = data.spec_yaml || JSON.stringify(data.spec || data, null, 2);
    copyStatusEl.textContent = "";
  } catch (error) {
    resultEl.textContent = JSON.stringify({ ok: false, error: String(error) }, null, 2);
    copyStatusEl.textContent = "";
  } finally {
    isProcessing = false;
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = "Отправить на обработку";
  }
}

analyzeBtn.addEventListener("click", analyzeSelectedFile);

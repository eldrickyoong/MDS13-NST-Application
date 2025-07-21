/**
 * =============================
 * AI Style Transfer Main Script
 * =============================
 * Handles upload previews, style thumbnail loading,
 * model selection, dropzone functionality, and form submission.
 */

// DOM Selectors
const resultContainer = document.getElementById("result-container");
const resultImage = document.getElementById("stylized-image");
const uploadSection = document.querySelector(".upload-section");
const contentInput = document.getElementById("content-upload");
const modelSelector = document.getElementById("model-selector");
const modelInput = document.getElementById("selected-model-name");
const fileInput = document.getElementById("content-upload");
const previewImage = document.getElementById("preview-image-content");
const previewContainer = document.getElementById("preview-container-content");
const fileName = document.getElementById("file-name-content");


/**
 * ========== Image Generation ==========
 */
async function generateStylizedImage() {
  if (!contentInput.files.length) {
    alert("Please upload a content image.");
    return;
  }

  const formData = new FormData();
  formData.append("content", contentInput.files[0]);
  formData.append("model_name", modelInput.value);
  formData.append("style_path", document.getElementById("selected-style-path").value);

  try {
    const response = await fetch("/stylize/", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) throw new Error("Stylization failed");

    const blob = await response.blob();
    resultImage.src = URL.createObjectURL(blob);
    resultContainer.style.display = "block";
    uploadSection.classList.add("shift-up");
  } catch (error) {
    console.error("Error:", error);
    alert("Failed to stylize image.");
  }
}


/**
 * ========== Style Thumbnails ========== 
 */
function loadStyleThumbnails(modelName) {
  fetch(`/style-images?model=${modelName}`)
    .then(res => res.json())
    .then(images => {
      const gallery = document.getElementById("style-gallery");
      gallery.innerHTML = "";

      const preview = document.getElementById("preview-image-style");
      const label = document.getElementById("upload-content-style");
      const hiddenInput = document.getElementById("selected-style-path");

      images.forEach((src) => {
        const img = document.createElement("img");
        img.src = src;
        img.classList.add("style-thumb");

        img.addEventListener("click", () => {
          document.querySelectorAll(".style-thumb").forEach(el => el.classList.remove("selected"));
          img.classList.add("selected");
          preview.src = src;
          preview.style.display = "block";
          label.style.display = "none";
          hiddenInput.value = src;
        });

        gallery.appendChild(img);
      });
    })
    .catch(err => console.error("Failed to load style images:", err));
}

/**
 * ========== Upload Function ========== 
 */

function setupUploadCard({
  areaId,
  dropAreaSelectorId,
  previewId,
  labelId,
  fileNameId = null,
  containerId = null,
}) {
  const input = document.getElementById(areaId);
  const dropArea = typeof dropAreaSelectorId === "string"
    ? document.querySelector(dropAreaSelectorId)
    : dropAreaSelectorId;

  const label = document.getElementById(labelId);
  const fileName = fileNameId ? document.getElementById(fileNameId) : null;
  const container = containerId ? document.getElementById(containerId) : null;

  // check if event is coming from style or content box
  const type = areaId.includes("style") ? "style" : "content";

  // click listener
  dropArea.addEventListener("click", () => input.click());

  // drag & drop listener
  dropArea.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropArea.classList.add("dragover");
  });

  dropArea.addEventListener("dragleave", () => {
    dropArea.classList.remove("dragover");
  });

  dropArea.addEventListener("drop", (e) => {
    e.preventDefault();
    dropArea.classList.remove("dragover");
    const file = e.dataTransfer.files[0];
    if (!file) return;
    input.files = e.dataTransfer.files;
    showPreview(file);
  });
  
  // Input change
  input.addEventListener("change", () => {
    if (!input.files.length) return;
    showPreview(input.files[0]);
  });

  // --- Preview Logic ---
  function showPreview(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = document.getElementById(previewId);
      img.src = e.target.result;
      img.style.display = "block";
      if (label) label.style.display = "none";
      if (fileName) fileName.textContent = file.name;
      if (container) container.style.display = "flex";

      // Wait until the image is fully loaded before reading dimensions
      img.onload = () => {
        const width = img.naturalWidth;
        const height = img.naturalHeight;
        fileName.textContent = `${file.name} (${width}×${height})`;
      };

      // Show the overlay + mark as active
      document.getElementById(dropAreaSelectorId).classList.add("has-image");
    };
    reader.readAsDataURL(file);
  }
}

function resetUpload(type) {
  document.getElementById(`${type}-upload`).value = "";
  document.getElementById(`preview-image-${type}`).src = "";
  document.getElementById(`preview-container-${type}`).style.display = "none";
  document.getElementById(`upload-${type}-display`).style.display = "flex";
  document.getElementById(`file-name-${type}`).textContent = "";

  // remove overlay trigger
  document.getElementById(`${type}-box`).classList.remove("has-image");
}

/**
 * ========== Range Sync ==========
 */
const dimensionSlider = document.getElementById("dimension-slider");
const dimensionValue = document.getElementById("dimension-value");

dimensionSlider.addEventListener("input", () => {
  dimensionValue.value = dimensionSlider.value;
});


/**
 * ========== Modal Logic ==========
 */
function confirmClear() {
  document.getElementById("clear-modal").style.display = "flex";
}

function closeModal() {
  document.getElementById("clear-modal").style.display = "none";
}

function executeClear() {
  closeModal();
  resetAll();
}


/**
 * ========== Reset All ==========
 */
function resetAll() {
  resetDropzone();
  document.getElementById("style-upload").value = "";
  document.getElementById("preview-image-style").style.display = "none";
  document.getElementById("selected-style-path").value = "";
  document.getElementById("style-gallery").innerHTML = "";

  modelSelector.selectedIndex = 0;
  modelInput.value = modelSelector.value;

  loadStyleThumbnails(modelSelector.value);
}


/**
 * ========== Toggle Expand for Style Section ==========
 */
function toggleStyleSection(button) {
  const expanded = button.getAttribute("aria-expanded") === "true";
  const galleryWrapper = button.nextElementSibling;

  button.setAttribute("aria-expanded", !expanded);
  galleryWrapper.classList.toggle("collapsed");

  if (!expanded && document.getElementById("style-gallery").children.length === 0) {
    loadStyleThumbnails(modelSelector.value);
  }
}

/**
 * ========== Init ==========
 */
window.addEventListener("DOMContentLoaded", () => {

  modelSelector.addEventListener("change", () => {
    modelInput.value = modelSelector.value;
    loadStyleThumbnails(modelSelector.value);
  });

  loadStyleThumbnails(modelSelector.value);

  document.getElementById("full-overlay-content").addEventListener("click", (e) => {
    e.stopPropagation();
    resetUpload("content");
  });

  document.getElementById("full-overlay-style").addEventListener("click", (e) => {
    e.stopPropagation();
    resetUpload("style");
  });
});

window.addEventListener("DOMContentLoaded", () => {
  setupUploadCard({
    areaId: "content-upload", 
    dropAreaSelectorId: "content-box",
    previewId: "preview-image-content",
    labelId: "upload-content-display",
    fileNameId: "file-name-content",
    containerId: "preview-container-content",
  });

  setupUploadCard({
    areaId: "style-upload",
    dropAreaSelectorId: "style-box", 
    previewId: "preview-image-style",
    labelId: "upload-content-style",
    fileNameId: "file-name-style",
    containerId: "preview-container-style"
  });

  // Load styles when a model is selected
  modelSelector.addEventListener("change", () => {
    modelInput.value = modelSelector.value;
    loadStyleThumbnails(modelSelector.value);
  });

  // Initial load
  loadStyleThumbnails(modelSelector.value);
});

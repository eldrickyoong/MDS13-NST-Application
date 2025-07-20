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
const previewImage = document.getElementById("preview-image");
const previewContainer = document.getElementById("preview-container");
const dropzone = document.getElementById("dropzone-content");
const dropzoneDisplay = document.getElementById("dropzone-display");
const fileName = document.getElementById("file-name");


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

      const preview = document.getElementById("preview-style");
      const label = document.getElementById("label-style");
      const hiddenInput = document.getElementById("selected-style-path");

      images.forEach((src, index) => {
        const img = document.createElement("img");
        img.src = src;
        img.classList.add("style-thumb");

        if (index === 0) {
          img.classList.add("selected");
          preview.src = src;
          preview.style.display = "block";
          label.style.display = "none";
          if (hiddenInput) hiddenInput.value = src;
        }

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
 * ========== Dropzone and Preview ========== 
 */
document.getElementById("remove-btn").addEventListener("click", (e) => {
  e.stopPropagation();
  resetDropzone();
});

dropzone.addEventListener("click", () => fileInput.click());

dropzone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropzone.classList.add("dragover");
});

dropzone.addEventListener("dragleave", () => {
  dropzone.classList.remove("dragover");
});

dropzone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropzone.classList.remove("dragover");
  fileInput.files = e.dataTransfer.files;
  handlePreview(fileInput.files[0]);
});

fileInput.addEventListener("change", () => {
  if (fileInput.files.length > 0) {
    handlePreview(fileInput.files[0]);
  }
});

function handlePreview(file) {
  const reader = new FileReader();
  reader.onload = (e) => {
    previewImage.src = e.target.result;
    fileName.textContent = file.name;
    dropzoneDisplay.style.display = "none";
    previewContainer.style.display = "flex";
  };
  reader.readAsDataURL(file);
}

function resetDropzone() {
  fileInput.value = "";
  dropzoneDisplay.style.display = "flex";
  previewContainer.style.display = "none";
  previewImage.src = "";
  fileName.textContent = "";
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
  document.getElementById("preview-style").style.display = "none";
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
  function previewImage(id, previewId, labelId) {
    const input = document.getElementById(id);
    const preview = document.getElementById(previewId);
    const label = document.getElementById(labelId);

    input.addEventListener("change", () => {
      const file = input.files[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = (e) => {
        preview.src = e.target.result;
        preview.style.display = "block";
        label.style.display = "none";
      };
      reader.readAsDataURL(file);
    });
  }

  previewImage("content-upload", "preview-content", "label-content");
  previewImage("style-upload", "preview-style", "label-style");

  modelSelector.addEventListener("change", () => {
    modelInput.value = modelSelector.value;
    loadStyleThumbnails(modelSelector.value);
  });

  loadStyleThumbnails(modelSelector.value);
});
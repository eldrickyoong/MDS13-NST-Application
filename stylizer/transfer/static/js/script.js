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
const modelInput = document.getElementById("selected-model-value");
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

  resultContainer.style.display = "flex";

  uploadSection.classList.add("shift-up");
  uploadSection.classList.add("shrink");

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
    resultImage.style.display = "block";

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
      const hiddenInput = document.getElementById("selected-style-path");

      images.forEach((src) => {
        const img = document.createElement("img");
        img.src = src;
        img.classList.add("style-thumb");

        img.addEventListener("click", () => {
          document.querySelectorAll(".style-thumb").forEach(el => el.classList.remove("selected"));
          img.classList.add("selected");
          showPreview(src, "style");
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
  dropAreaSelectorId
}) {
  const input = document.getElementById(areaId);
  const dropArea = document.getElementById(dropAreaSelectorId);
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
    showPreview(file, type);
  });
  
  // Input change
  input.addEventListener("change", () => {
    if (!input.files.length) return;
    showPreview(input.files[0], type);
  });

}

// --- Preview Logic ---
function showPreview(input, type) {
  const previewId = `preview-image-${type}`;
  const label = document.getElementById(`upload-${type}-display`);
  const fileName = document.getElementById(`file-name-${type}`);
  const container = document.getElementById(`preview-container-${type}`);
  const dropAreaSelectorId = `${type}-box`;

  const img = document.getElementById(previewId);

  const setImage = (src, name) => {
    let imgName = name;

    // if image is from a style thumbnail, extract from the url
    if (typeof input === "string") imgName = src.split("/").pop();
    if (img) img.src = src;
    img.style.display = "block";
    if (label) label.style.display = "none";
    if (container) container.style.display = "flex";

    img.onload = () => {
      const width = img.naturalWidth;
      const height = img.naturalHeight;
      if (fileName) fileName.textContent = `${imgName} (${width}×${height})`;
    };

    // Show the overlay + mark as active
    document.getElementById(dropAreaSelectorId).classList.add("has-image");
  };

  if (typeof input === "string") {
    // input is a URL
    setImage(input, "Style");
  } else {
    // input is a File
    const reader = new FileReader();
    reader.onload = (e) => setImage(e.target.result, input.name);
    reader.readAsDataURL(input);
  }
}

// -- Reset Upload Logic ---
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
// const dimensionSlider = document.getElementById("dimension-slider");
// const dimensionValue = document.getElementById("dimension-value");

// dimensionSlider.addEventListener("input", () => {
//   dimensionValue.value = dimensionSlider.value;
// });


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
  document.getElementById("style-upload").value = "";
  document.getElementById("style-gallery").innerHTML = "";

  // modelSelector.selectedIndex = 0;
  // modelInput.value = modelSelector.value;

  // loadStyleThumbnails(modelSelector.value);
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
    loadStyleThumbnails(modelInput.value);
  }
}

/**
 * ========== Init ==========
 */
window.addEventListener("DOMContentLoaded", () => {

  const modelName = document.getElementById("selected-model-value");
  loadStyleThumbnails(modelName.value);

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
    dropAreaSelectorId: "content-box"
  });

  setupUploadCard({
    areaId: "style-upload",
    dropAreaSelectorId: "style-box",
  });

});

/**
 * ========== Dropdown Box ==========
 */
function setupDropdown({ dropdownId, selectedId, optionsId, hiddenInputId, onChange = null }) {
  const dropdown = document.getElementById(dropdownId);
  const selected = document.getElementById(selectedId);
  const options = document.getElementById(optionsId);
  const hiddenInput = document.getElementById(hiddenInputId);

  dropdown.addEventListener("click", (e) => {
    if (e.target === selected) {
      dropdown.classList.toggle("open");
    }
  });

  options.addEventListener("click", (e) => {
    if (e.target.classList.contains("dropdown-option")) {
      dropdown.classList.remove("open");

      const value = e.target.dataset.value;
      selected.textContent = e.target.textContent;
      hiddenInput.value = value;

      options.querySelectorAll(".dropdown-option").forEach(opt => opt.classList.remove("selected"));
      e.target.classList.add("selected");

      if (onChange) onChange(value);
    }
  });

  document.addEventListener("click", (e) => {
    if (!dropdown.contains(e.target)) {
      dropdown.classList.remove("open");
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  setupDropdown({
    dropdownId: "model-dropdown",
    selectedId: "selected-model",
    optionsId: "model-options",
    hiddenInputId: "selected-model-value",
    onChange: loadStyleThumbnails
  });

  setupDropdown({
    dropdownId: "quality-dropdown",
    selectedId: "selected-quality",
    optionsId: "quality-options",
    hiddenInputId: "selected-quality-value",
    onChange: (val) => console.log("Quality selected:", val)
  });
});

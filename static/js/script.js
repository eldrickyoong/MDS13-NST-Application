async function generateStylizedImage() {
  const resultContainer = document.getElementById("result-container");
  const resultImage = document.getElementById("stylized-image");
  const uploadSection = document.querySelector(".upload-section");

  const contentInput = document.getElementById("content-upload");

  if (!contentInput.files.length) {
    alert("Please upload a content image.");
    return;
  }

  const formData = new FormData();
  formData.append("content", contentInput.files[0]);
  formData.append("model_name", modelInput.value);
  formData.append("style_path", document.getElementById("selected-style-path").value);


  try {
    const response = await fetch("/stylize", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) throw new Error("Stylization failed");

    const blob = await response.blob();
    const resultUrl = URL.createObjectURL(blob);

    resultImage.src = resultUrl;
    resultContainer.style.display = "block";
    uploadSection.classList.add("shift-up");
  } catch (error) {
    console.error("Error:", error);
    alert("Failed to stylize image.");
  }
}

// == Load style thumbnails based on model ===
function loadStyleThumbnails(modelName) {
  fetch(`/style-images?model=${modelName}`)
    .then(res => res.json())
    .then(images => {
      const gallery = document.getElementById('style-gallery');
      gallery.innerHTML = ""; // Clear previous thumbnails
      const preview = document.getElementById('preview-style');
      const label = document.getElementById('label-style');
      const hiddenInput = document.getElementById('selected-style-path');

      images.forEach((src, index) => {
        const img = document.createElement('img');
        img.src = src;
        img.classList.add('style-thumb');

        if (index === 0) {
          img.classList.add('selected');
          preview.src = src;
          preview.style.display = 'block';
          label.style.display = 'none';
          if (hiddenInput) hiddenInput.value = src;
        }

        img.addEventListener('click', () => {
          document.querySelectorAll('.style-thumb').forEach(el => el.classList.remove('selected'));
          img.classList.add('selected');

          preview.src = src;
          preview.style.display = 'block';
          label.style.display = 'none';

          hiddenInput.value = src;
        });

        gallery.appendChild(img);
      });
    })
    .catch(err => console.error("Failed to load style images:", err));
}

const modelSelector = document.getElementById("model-selector");
const modelInput = document.getElementById("selected-model-name");

modelSelector.addEventListener("change", () => {
  modelInput.value = modelSelector.value;
  loadStyleThumbnails(modelSelector.value); // already working
});

window.addEventListener('DOMContentLoaded', () => { 
  // === Image Uploade Preview ===
  function previewImage(inputId, previewId, labelId) {
    const input = document.getElementById(inputId);
    const preview = document.getElementById(previewId);
    const label = document.getElementById(labelId);

    input.addEventListener('change', () => {
      const file = input.files[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = e => {
        preview.src = e.target.result;
        preview.style.display = 'block';
        label.style.display = 'none'; // hide the label after upload
      };
      reader.readAsDataURL(file);
    });
  }

  previewImage("content-upload", "preview-content", "label-content");
  previewImage("style-upload", "preview-style", "label-style");

  // === style collapse section ===
  const toggleBtn = document.getElementById("toggle-style-btn");
  const styleGallery = document.getElementById("style-gallery");

  toggleBtn.addEventListener("click", () => {
    styleGallery.classList.toggle("collapsed");
    toggleBtn.textContent = styleGallery.classList.contains("collapsed") ? "▼" : "▲";
  });

  // === load style thumbnails based on model
  const modelSelector = document.getElementById("model-selector");
  modelSelector.addEventListener("change", () => {
    const selectedModel = modelSelector.value;
    loadStyleThumbnails(selectedModel);
  });

  // Load default model on startup
  loadStyleThumbnails(modelSelector.value);

});

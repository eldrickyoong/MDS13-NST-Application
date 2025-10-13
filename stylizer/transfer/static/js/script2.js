const form = document.querySelector("form");
const fileInput = form.querySelector(".file-input");
const uploadIcon = form.querySelector(".upload-icon");
const uploadText = form.querySelector("p");
const imgWrapper = form.querySelector(".img-wrapper");
const img = imgWrapper.querySelector("img");
const uploadSection = document.querySelector(".upload-section");
const modelInput = document.getElementById("selected-model-value");

form.addEventListener("click", () => {
    fileInput.click();
});

fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];
    if (!file) return;

    if (!file.type.startsWith("image/")) {
        alert("Please select an image file!");
        return;
    }

    const reader = new FileReader();
    reader.onload = () => {
        img.src = reader.result;
        imgWrapper.style.display = "inline-block";

        // hide upload icon and text
        uploadIcon.style.display = "none";
        uploadText.style.display = "none";
    };
    reader.readAsDataURL(file);
});

// Remove image on click
imgWrapper.addEventListener("click", (e) => {
    e.stopPropagation();
    imgWrapper.style.display = "none";
    img.src = "";
    uploadIcon.style.display = "inline-block";
    uploadText.style.display = "block";
    fileInput.value = "";
});

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

const dropdown = document.querySelector('.dropdown');
const button = document.querySelector('.dropdown-btn');
const options = document.querySelectorAll('.style-option');
const styleBox = document.querySelector('.style-box img'); // or your result box img

button.addEventListener('click', (e) => {
    e.stopPropagation();
    dropdown.classList.toggle('active');
});

// Close dropdown when clicking outside
document.addEventListener('click', (event) => {
    if (!dropdown.contains(event.target)) {
        dropdown.classList.remove('active');
    }
});

options.forEach(option => {
    option.addEventListener('click', () => {
        if (styleBox) styleBox.src = option.src;
        button.textContent = `Selected Style: ${option.alt}`;
        dropdown.classList.remove('active');
    });
});

document.addEventListener("DOMContentLoaded", function() {
    const styleOptions = document.querySelectorAll(".style-option");
    const selectedStylePreview = document.querySelector(".selected-style-preview");
    const dropdownBtn = document.querySelector(".dropdown-btn");
    const dropdownContent = document.querySelector(".dropdown-content");

    // Toggle dropdown visibility
    dropdownBtn.addEventListener("click", function(e) {
        e.stopPropagation();
        dropdownContent.classList.toggle("show");
    });

    // Close dropdown when clicking outside
    document.addEventListener("click", function(e) {
        if (!dropdownContent.contains(e.target) && !dropdownBtn.contains(e.target)) {
            dropdownContent.classList.remove("show");
        }
    });

    // When user clicks on a style image
    styleOptions.forEach(option => {
        option.addEventListener("click", function() {
            // Clear existing content
            selectedStylePreview.innerHTML = "";

            // Add selected image
            const img = document.createElement("img");
            img.src = this.src;
            img.alt = this.alt;
            img.classList.add("selected-style-img");

            // Add image and caption
            selectedStylePreview.appendChild(img);
            const caption = document.createElement("p");
            caption.textContent = this.alt;
            selectedStylePreview.appendChild(caption);

            // Close dropdown
            dropdownContent.classList.remove("show");
        });
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

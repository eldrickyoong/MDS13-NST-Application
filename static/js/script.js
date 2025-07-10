function generateStylizedImage() {
  const resultContainer = document.getElementById("result-container");
  const resultImage = document.getElementById("stylized-image");

  // Example: show a sample image
  resultImage.src = "/static/sample-images/lion_test.jpg";
  resultContainer.style.display = "block";
}

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

  // == Load and Select Style Thumbnails ===
  fetch('/style-images')
    .then(res => {
      console.log("Response from /style-images:", res);
      return res.json();
    })
    .then(images => {
      console.log("Image list received:", images);

      const gallery = document.getElementById('style-gallery');
      const preview = document.getElementById('preview-style');
      const label = document.getElementById('label-style');
      const hiddenInput = document.getElementById('selected-style-path');
      
      if (!gallery) {
        console.error("style-gallery not found in the DOM");
        return;
      }

      images.forEach((src, index) => {
        console.log("Adding image:", src);

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
          if (hiddenInput) hiddenInput.value = src;
        });

        gallery.appendChild(img);
      });
    })
    .catch(err => console.error("Failed to load style images:", err));

  // async function generateStylizedImage() {
  //   const contentInput = document.getElementById("content-upload");
  //   const selectedStylePath = document.getElementById("selected-style-path").value;

  //   if (!contentInput.files.length || !selectedStylePath) {
  //     alert("Please upload a content image and select a style.");
  //     return;
  //   }

  //   const formData = new FormData();
  //   formData.append("content", contentInput.files[0]);
  //   formData.append("style_path", selectedStylePath);

  //   try {
  //     const response = await fetch("/stylize", {
  //       method: "POST",
  //       body: formData,
  //     });

  //     if (!response.ok) {
  //       throw new Error("Stylization failed");
  //     }

  //     const blob = await response.blob();
  //     const resultUrl = URL.createObjectURL(blob);

  //     const resultImage = document.getElementById("stylized-image");
  //     resultImage.src = resultUrl;
  //     resultImage.style.display = "block";
  //   } catch (error) {
  //     console.error("Error generating image:", error);
  //     alert("Something went wrong!");
  //   }
  // }

});

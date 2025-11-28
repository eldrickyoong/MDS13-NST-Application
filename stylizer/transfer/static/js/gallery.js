// static/js/gallery.js

// Populates gallery page based on images in /media/user_gallery/
document.addEventListener("DOMContentLoaded", () => {
  const galleryBody = document.getElementById("galleryBody");
  const galleryGrid = document.getElementById("style-gallery");

  fetch("/gallery-images/")
    .then((res) => res.json())
    .then((images) => {
      if (!images.length) {
        galleryBody.setAttribute("data-empty", "true");
        return;
      }

      galleryBody.removeAttribute("data-empty");

      images.forEach((src) => {
        const tile = document.createElement("article");
        tile.className = "tile";

        // create inner elements
        const thumb = document.createElement("div");
        thumb.className = "thumb";
        const img = document.createElement("img");
        img.src = src;
        img.alt = "Generated artwork";
        img.loading = "lazy";

        thumb.appendChild(img);

        tile.appendChild(thumb);
        galleryGrid.appendChild(tile);
      });

      // reveal animation when scrolled into view
      const io = new IntersectionObserver(
        (entries) => {
          entries.forEach((e) => {
            if (e.isIntersecting) {
              e.target.classList.add("is-visible");
              io.unobserve(e.target);
            }
          });
        },
        { root: galleryBody, threshold: 0.05 }
      );

      document.querySelectorAll(".tile").forEach((t) => io.observe(t));
    })
    .catch((err) => {
      console.error("Failed to load gallery images:", err);
      galleryBody.setAttribute("data-empty", "true");
    });
});

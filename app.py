from flask import Flask, request, jsonify, send_file, render_template
# import tensorflow as tf
# import tensorflow_hub as hub
import numpy as np
from PIL import Image
import io
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
OUTPUT_PATH = "static/stylized.png"
STYLE_MODEL_URL = "https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2"

# model = hub.load(STYLE_MODEL_URL)

STYLE_IMAGE_FOLDER = os.path.join("static", "images", "style-images")

@app.route("/create")
def create():
    return render_template("create_2.html")

@app.route("/style-images")
def list_styles():
    try:
        files = [
            f for f in os.listdir(STYLE_IMAGE_FOLDER)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ]
        files.sort(key=lambda f: os.path.getmtime(os.path.join(STYLE_IMAGE_FOLDER, f)), reverse=True)
        
        paths = [f"/static/images/style-images/{f}" for f in files]
        return jsonify(paths)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# @app.route("/stylize", methods=["POST"])
# def stylize():
#     # Ignore user-uploaded content for now
#     sample_content_path = "static/test-content.jpg"
#     sample_style_path = "static/images/style-images/ben_giles.jpg"

#     with open(sample_content_path, "rb") as f:
#         content = load_image_pillow(f.read())
#     with open(sample_style_path, "rb") as f:
#         style = load_image_pillow(f.read())

#     stylized = model(content, style)[0]
#     img = tf.image.convert_image_dtype(stylized[0], dtype=tf.uint8)

#     buf = io.BytesIO()
#     Image.fromarray(img.numpy()).save(buf, format="PNG")
#     buf.seek(0)
#     return send_file(buf, mimetype="image/png")

def load_image_pillow(path, size=(512, 512)):
    img = Image.open(path).convert("RGB")
    img = img.resize(size)  # or use thumbnail() to maintain aspect ratio
    img_array = np.asarray(img).astype("float32") / 255.0  # normalize to [0,1]
    img_array = np.expand_dims(img_array, axis=0)  # add batch dimension
    return img_array

# @app.route("/stylize", methods=["POST"])
# def stylize():
#     content_img = request.files["content"]
#     style_img = request.files["style"]
#     content = load_image(content_img.read())
#     style = load_image(style_img.read())
#     stylized = model(content, style)[0]
#     img = tf.image.convert_image_dtype(stylized[0], dtype=tf.uint8)
#     buf = io.BytesIO()
#     Image.fromarray(img.numpy()).save(buf, format="PNG")
#     buf.seek(0)
#     with open(OUTPUT_PATH, 'wb') as f:
#         f.write(buf.read())
#     return send_file(OUTPUT_PATH, mimetype='image/png')

if __name__ == "__main__":
    # os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)

from flask import Flask, request, jsonify, send_file
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
from PIL import Image
import io
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
OUTPUT_PATH = "static/stylized.png"
STYLE_MODEL_URL = "https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2"

model = hub.load(STYLE_MODEL_URL)

def load_image(image_bytes, max_dim=512):
    img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    img.thumbnail((max_dim, max_dim))
    img = np.array(img) / 255.0
    return tf.constant(img, dtype=tf.float32)[tf.newaxis, ...]

@app.route("/stylize", methods=["POST"])
def stylize():
    content_img = request.files["content"]
    style_img = request.files["style"]
    content = load_image(content_img.read())
    style = load_image(style_img.read())
    stylized = model(content, style)[0]
    img = tf.image.convert_image_dtype(stylized[0], dtype=tf.uint8)
    buf = io.BytesIO()
    Image.fromarray(img.numpy()).save(buf, format="PNG")
    buf.seek(0)
    with open(OUTPUT_PATH, 'wb') as f:
        f.write(buf.read())
    return send_file(OUTPUT_PATH, mimetype='image/png')

if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)

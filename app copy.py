from flask import Flask, request, jsonify, send_file, render_template, Response
import numpy as np
from PIL import Image
import io
import os
import time
import threading
from shared.state import progress_value, last_result
import shared.state as state

from style_transfer_models.johnson_fast_style.inference import stylize_image_pil, load_model
from style_transfer_models.gatys_iterative_style.inference import neural_style_transfer_from_pil

gatys_config = {
    "height": 400,
    "content_weight": 1e5,
    "style_weight": 3e4,
    "tv_weight": 1e0,
    "optimizer": "lbfgs",
    "model": "vgg19",
    "init_method": "content",
}

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
OUTPUT_PATH = "static/stylized.png"

@app.route("/create")
def create():
    return render_template("create_2.html")

@app.route("/progress")
def progress():
    def generate():
        while state.progress_value < 100:
            print(f"Sending progress: {state.progress_value}")
            yield f"data: {state.progress_value}\n\n"
            time.sleep(0.4)  # adjust for smoother UI
        yield f"data: 100\n\n"
    return Response(generate(), mimetype='text/event-stream')

@app.route("/style-images")
def style_images():
    model_name = request.args.get("model", "johnson_fast_style")
    folder = os.path.join("static", "images", model_name)
    
    try:
        files = [
            f"/static/images/{model_name}/{f}"
            for f in os.listdir(folder)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ]
        return jsonify(files)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/stylize", methods=["POST"])
def stylize():
    state.progress_value = 0
    
    content_file = request.files.get("content")
    model_name = request.form.get("model_name")
    style_path = request.form.get("style_path")

    if not content_file or not model_name or not style_path:
        return "Missing content, model, or style", 400

    content_img = Image.open(content_file).convert("RGB")
    style_img = Image.open(style_path.lstrip("/")).convert("RGB")  # strip leading slash

    def background_task():
        if model_name == "johnson_fast_style":
            # Extract style image name from the path
            style_filename = os.path.basename(style_path)         # e.g. "mosaic.jpg"
            style_base = os.path.splitext(style_filename)[0]      # e.g. "mosaic"
            
            # Build the model path dynamically
            model_path = os.path.join("style_transfer_models", "johnson_fast_style", "binaries", f"{style_base}.pth")
            model, device = load_model(model_path)
            # from style_transfer_models.johnson_fast_style.inference import stylize_johnson
            
            if not os.path.exists(model_path):
                return f"Model weights not found for style: {style_base}", 400
            
            result_img = stylize_image_pil(content_img, model, device)
            if isinstance(result_img, Image.Image):
                state.last_result = result_img
                state.progress_value = 100
                print("Johnson result saved to state.")
            else:
                print("stylize_image_pil() returned None or invalid image")
        elif model_name == "gatys_iterative_style":
            # from style_transfer_models.gatys_iterative_style.inference import stylize_gatys
            result_img = neural_style_transfer_from_pil(content_img, style_img, gatys_config)
            state.last_result = result_img
    
    thread = threading.Thread(target=background_task)
    thread.start()

    return "started", 202

    # buf = io.BytesIO()
    # result_img.save(buf, format="PNG")
    # buf.seek(0)
    # return send_file(buf, mimetype="image/png")

@app.route("/result")
def result():
    if state.last_result is None:
        return "Result not ready", 404

    buf = io.BytesIO()
    state.last_result.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

def load_image_pillow(path, size=(512, 512)):
    img = Image.open(path).convert("RGB")
    img = img.resize(size)  # or use thumbnail() to maintain aspect ratio
    img_array = np.asarray(img).astype("float32") / 255.0  # normalize to [0,1]
    img_array = np.expand_dims(img_array, axis=0)  # add batch dimension
    return img_array


if __name__ == "__main__":
    # os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)

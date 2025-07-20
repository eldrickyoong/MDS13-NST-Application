from pathlib import Path
from PIL import Image
from style_transfer_models.johnson_fast_style.inference import stylize_image_pil, load_model
from style_transfer_models.gatys_iterative_style.inference import neural_style_transfer
from django.conf import settings
import matplotlib.pyplot as plt

VALID_MODELS = ['johnson_fast_style', 'gatys_iterative_style']

gatys_config = {
    "height": 400,
    "content_weight": 1e5,
    "style_weight": 3e4,
    "tv_weight": 1e0,
    "optimizer": "lbfgs",
    "model": "vgg19",
    "init_method": "content",
    "img_format": (4, '.jpg')
}

def stylize_image(content_file, style_path_str, model_name):
    
    if model_name not in VALID_MODELS:
        raise ValueError("Unknown model name")
    
    # Load content image
    content_img = Image.open(content_file).convert("RGB")

    # Convert style path string to local path and open style image
    style_path_rel = style_path_str.lstrip('/')
    style_path = Path(settings.BASE_DIR) / "transfer" / Path(style_path_rel)
    style_img = Image.open(style_path).convert("RGB")

    if model_name == "johnson_fast_style":
        # Extract base name (e.g., 'candy' from 'candy.jpg')
        style_base = style_path.stem
        model_path = Path("style_transfer_models/johnson_fast_style/binaries") / f"{style_base}.pth"

        if not model_path.exists():
            raise FileNotFoundError(f"Model weights not found: {model_path}")

        model, device = load_model(model_path)
        return stylize_image_pil(content_img, model, device)

    else:
        return neural_style_transfer(content_file, style_img, gatys_config)


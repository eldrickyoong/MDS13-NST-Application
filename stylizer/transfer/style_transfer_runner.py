from pathlib import Path
from PIL import Image
from django.conf import settings
import matplotlib.pyplot as plt

from style_transfer.johnson_fast_style.inference import stylize_image_pil, load_model
from style_transfer.gatys_iterative_style.inference import neural_style_transfer

from style_transfer.johnson import JohnsonStyleTransferModel
from style_transfer.utils import image_to_tensor, tensor_to_pil
    

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
    content_tensor = image_to_tensor(content_img)

    # Convert style path string to local path and open style image
    style_path_rel = style_path_str.lstrip('/')
    style_path = Path(__file__).resolve().parent.parent / "transfer" / Path(style_path_rel)
    style_img = Image.open(style_path).convert("RGB")

    if model_name == "johnson_fast_style":
        # Extract base name (e.g., 'candy' from 'candy.jpg')
        style_base = style_path.stem
        model_path = Path(__file__).resolve().parent.parent / "style_transfer" / "johnson_fast_style" / "binaries" / f"{style_base}.pth"
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model weights not found: {model_path}")
        
        model = JohnsonStyleTransferModel()
        model.load_model(model_path)
        
        output_tensor = model.stylize(content_tensor)
        output_image = tensor_to_pil(output_tensor)


        # model, device = load_model(model_path)
        # output_image = stylize_image_pil(content_img, model, device)
        
        return output_image

    else:
        return neural_style_transfer(content_file, style_img, gatys_config)
    
if __name__ == "__main__":
    # PS C:\Users\eldri\My Drive\Monash\Y3S2\FIT3164 Data Science Project 2\MDS13-NST-Application\stylizer> python -m transfer.style_transfer_runner
    content_file = r'C:\Users\eldri\My Drive\Monash\Y3S2\FIT3164 Data Science Project 2\MDS13-NST-Application\stylizer\transfer\static\images\content-images\figures.jpg'
    style_path = r'C:\Users\eldri\My Drive\Monash\Y3S2\FIT3164 Data Science Project 2\MDS13-NST-Application\stylizer\transfer\static\images\johnson_fast_style\starry.jpg'
    model_name = 'johnson_fast_style'
    image = stylize_image(content_file, style_path, model_name)
    image.show()


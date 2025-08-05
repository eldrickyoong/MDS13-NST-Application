from pathlib import Path
from PIL import Image
from django.conf import settings
import matplotlib.pyplot as plt
from style_transfer.johnson import JohnsonStyleTransferModel
from style_transfer.linear import LinearStyleTransferModel
from style_transfer.gatys import GatysStyleTransferModel
from style_transfer.utils import image_to_tensor, tensor_to_pil

VALID_MODELS = ['johnson_fast_style', 'gatys_iterative_style', 'linear_fast_style']

def stylize_image(content_file, model_name, style_file=None, style_path_str=None):

    if model_name not in VALID_MODELS:
            raise ValueError("Unknown model name")
    
    # Load content image
    content_img = Image.open(content_file).convert("RGB")
    content_tensor = image_to_tensor(content_img)

    # Convert style path string to local path and open style image
    if style_file:
        style_img = Image.open(style_file).convert("RGB")
    else:
        style_path_rel = style_path_str.lstrip('/')
        style_path = Path(__file__).resolve().parent.parent / "transfer" / Path(style_path_rel)
        style_img = Image.open(style_path).convert("RGB")
        
    style_tensor = image_to_tensor(style_img)
    
    model_base_path = Path(__file__).resolve().parent.parent / "style_transfer"

    if model_name == "johnson_fast_style":
        # Extract base name (e.g., 'candy' from 'candy.jpg')
        if not style_path_str:
            raise ValueError("Johnson model requires predefined style path")
        style_base = style_path.stem
        model_path = model_base_path / "johnson_fast_style" / "binaries" / f"{style_base}.pth"
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model weights not found: {model_path}")
        
        model = JohnsonStyleTransferModel()
        model.load_model(model_path)
    elif model_name == "linear_fast_style":
        
        model = LinearStyleTransferModel()
        model.load_model(model_base_path)

    else:
        model = GatysStyleTransferModel()
        model.load_model(model_base_path)
    
    output_tensor = model.stylize(content_tensor, style_tensor)
    output_image = tensor_to_pil(output_tensor)
    return output_image
    
if __name__ == "__main__":
    # PS C:\Users\eldri\My Drive\Monash\Y3S2\FIT3164 Data Science Project 2\MDS13-NST-Application\stylizer> python -m transfer.style_transfer_runner
    content_file = r'C:\Users\eldri\My Drive\Monash\Y3S2\FIT3164 Data Science Project 2\MDS13-NST-Application\stylizer\transfer\static\images\content-images\figures.jpg'
    style_path = r'C:\Users\eldri\My Drive\Monash\Y3S2\FIT3164 Data Science Project 2\MDS13-NST-Application\stylizer\transfer\static\images\johnson_fast_style\starry.jpg'
    model_name = 'gatys_iterative_style'
    image = stylize_image(content_file, style_path, model_name)
    image.show()


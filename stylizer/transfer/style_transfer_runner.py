from pathlib import Path
from PIL import Image
from django.conf import settings
from typing import Optional, List
import matplotlib.pyplot as plt
from style_transfer.johnson import JohnsonStyleTransferModel
from style_transfer.linear import LinearStyleTransferModel
from style_transfer.gatys import GatysStyleTransferModel
from style_transfer.utils import image_to_tensor, tensor_to_pil

VALID_MODELS = ['johnson_fast_style', 'gatys_iterative_style', 'linear_fast_style']
BINARIES_ROOT = Path(__file__).resolve().parent.parent / "style_transfer" / "johnson_fast_style" / "binaries"

def find_binary_for_style(
    style_name: str,
    binaries_root: Path = BINARIES_ROOT,
    suffix: str = ".pth",
) -> Optional[Path]:
    """
    Look in binaries_root for any file whose name contains the style_name
    and ends with the given suffix.
    If multiple matches exist, pick the most recently modified file.
    Returns None if nothing matches.
    """
    if not binaries_root.exists():
        raise ValueError(f'{binaries_root} does not exist')
    
    candidates: List[Path] = [
        p for p in binaries_root.glob(f"*{suffix}")
        if style_name.lower() in p.stem.lower()
    ]
    if not candidates:
        return None

    # Pick the newest by mtime
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]

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
    
        model_path = find_binary_for_style(str(style_path.stem))
        
        if not model_path or not model_path.exists():
            raise FileNotFoundError(f"Model weights not found: {style_path.stem, model_path}")
        
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
    model_name = 'johnson_fast_style'
    image = stylize_image(content_file, model_name, style_path_str=style_path)
    image.show()


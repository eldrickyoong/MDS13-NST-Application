from pathlib import Path
from PIL import Image
from typing import Optional, List
import torch

from style_engine.johnson import JohnsonStyleTransferModel
from style_engine.linear import LinearStyleTransferModel

PREDEFINED_ROOT = Path(__file__).resolve().parent.parent / "transfer" / "static" / "images" / "johnson_fast_style"
MODEL_ROOT = Path(__file__).resolve().parent.parent / "style_engine" / "backends" / "weights"

def find_binary_for_style(
    style_name: str,
    models_root = MODEL_ROOT,
    suffix: str = ".pth",
) -> Optional[Path]:
    """
    Look in binaries_root for any file whose name contains the style_name
    and ends with the given suffix.
    If multiple matches exist, pick the most recently modified file.
    Returns None if nothing matches.
    """
    if not models_root.exists():
        raise ValueError(f'{models_root} does not exist')
    
    candidates: List[Path] = [
        p for p in models_root.glob(f"*{suffix}")
        if style_name.lower() in p.stem.lower()
    ]
    if not candidates:
        return None
    
    return candidates[0]

def stylize_image(content_file, style_file=None, style_path_str: None | str = None):
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Load content image
    content_img = Image.open(content_file).convert("RGB")

    # Convert style path string to local path and open style image
    if style_file:
        style_img = Image.open(style_file).convert("RGB")
    else:
        style_name = Path(style_path_str).name
        style_path = PREDEFINED_ROOT / style_name
        style_img = None

    if style_path_str:
        model_path = find_binary_for_style(str(style_path.stem))
        
        model = JohnsonStyleTransferModel(device=device)
        model.load_model(model_path)
    else:
        model = LinearStyleTransferModel(device=device)
        model.load_model(MODEL_ROOT)

    output = model.stylize(content_img, style_img)
    return output


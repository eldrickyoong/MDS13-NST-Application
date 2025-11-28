from pathlib import Path
from PIL import Image
import torch

from style_engine.johnson import JohnsonStyleTransferModel
from style_engine.linear import LinearStyleTransferModel

MODEL_ROOT = (
    Path(__file__).resolve().parent.parent / "style_engine" / "backends" / "weights"
)


def stylize_image(
    content_file: str, style_file: None | str = None, style_path_str: None | str = None
) -> Image.Image:
    """
    Performs stylization via Johnson or Linear network, depending on input
    """

    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Load content image
    content_img: Image.Image = Image.open(content_file).convert("RGB")

    # Convert style path string to local path and open style image
    style_img: Image.Image | None = Image.open(style_file).convert("RGB") if style_file else None

    # Uses johnson model if input is a style_path_str (chosen from predefined styles)
    if style_path_str:
        style_name = Path(style_path_str).stem
        model_path = MODEL_ROOT / "johnson" / f"{style_name}.pth"

        model = JohnsonStyleTransferModel(device=device)
        model.load_model(model_path)
    else:
        model = LinearStyleTransferModel(device=device)
        model.load_model(MODEL_ROOT / "linear")

    output: Image.Image = model.stylize(content_img, style_img)
    return output

import torch
from style_transfer_models.johnson_fast_style.transformer_net import TransformerNet
from PIL import Image
from torchvision import transforms
import numpy as np

def stylize_image_pil(content_pil: Image.Image, model, device) -> Image.Image:
    transform = transforms.Compose([
        transforms.Resize((512, 512)),
        transforms.ToTensor(),
    ])
    content_tensor = transform(content_pil).unsqueeze(0).to(device)

    with torch.no_grad():
        output_tensor = model(content_tensor).cpu().clamp(0, 1)

    output_np = output_tensor.squeeze(0).numpy()
    output_np = np.transpose(output_np, (1, 2, 0))  # [H,W,C]
    output_img = Image.fromarray((output_np * 255).astype("uint8"))
    return output_img

def load_model(model_path):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = TransformerNet().to(device)
    state = torch.load(model_path, map_location=device)
    model.load_state_dict(state["state_dict"])
    model.eval()
    return model, device

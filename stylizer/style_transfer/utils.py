from PIL import Image
import torchvision.transforms as transforms
import torch

def image_to_tensor(pil_img, size=(512, 512)):
    transform = transforms.Compose([
        transforms.Resize(size) if size else lambda x: x,
        transforms.ToTensor(),
    ])
    return transform(pil_img).unsqueeze(0)

def tensor_to_pil(tensor):
    tensor = tensor.detach().squeeze(0).clamp(0, 1)
    return transforms.ToPILImage()(tensor.cpu())

import torch
from style_transfer.johnson_fast_style.transformer_net import TransformerNet
from .base import BaseStyleTransferModel
import numpy as np
from PIL import Image
import cv2 as cv
import torchvision.transforms as transforms

IMAGENET_MEAN_1 = np.array([0.485, 0.456, 0.406])
IMAGENET_STD_1 = np.array([0.229, 0.224, 0.225])

class JohnsonStyleTransferModel(BaseStyleTransferModel):
    def load_model(self, model_path):
      if model_path is None:
        raise ValueError("model_path is required for Johnson model.")
      self.model = TransformerNet().to(self.device)
      state = torch.load(model_path, map_location=self.device)
      self.model.load_state_dict(state["state_dict"], strict=True)
      self.model.eval()

    def preprocess(self, image):
      img = super().preprocess(image)
      transform = transforms.Compose([
          transforms.ToTensor(),
          transforms.Normalize(mean=IMAGENET_MEAN_1, std=IMAGENET_STD_1)
      ])
    
      img = transform(img).to(self.device)
      return img.unsqueeze(0)

    def stylize(self, content_img_tensor, style_img_tensor=None):
      input_tensor = self.preprocess(content_img_tensor)
      
      with torch.no_grad():
        output = self.model(input_tensor).to("cpu").numpy()[0]
        mean = IMAGENET_MEAN_1.reshape(-1, 1, 1)
        std = IMAGENET_STD_1.reshape(-1, 1, 1)
        output = (output * std) + mean  # de-normalize
        output = (np.clip(output, 0., 1.) * 255).astype(np.uint8)
        output = np.moveaxis(output, 0, 2)
      
      return Image.fromarray(output)
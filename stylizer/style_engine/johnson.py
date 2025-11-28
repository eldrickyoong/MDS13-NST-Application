"""
This module includes code adapted from external open-source repositories.
See `README.md` (Acknowledgement section) for full details.
"""

import torch
from style_engine.backends.johnson_fast.transformer_net import TransformerNet
from .base import BaseStyleTransferModel
import numpy as np
from PIL import Image
import torchvision.transforms as transforms

IMAGENET_MEAN_1 = np.array([0.485, 0.456, 0.406])
IMAGENET_STD_1 = np.array([0.229, 0.224, 0.225])


class JohnsonStyleTransferModel(BaseStyleTransferModel):
    """
    Class used for stylization via Johnson FFN, inherits BaseStyleTransferModel
    """

    @BaseStyleTransferModel.safe_load_wrapper
    def load_model(self, model_path):
        self.model = TransformerNet().to(self.device)
        state = torch.load(model_path, map_location=self.device)
        self.model.load_state_dict(state["state_dict"], strict=True)
        self.model.eval()

    def preprocess(self, image: Image.Image) -> torch.Tensor:
        """
        Preprocess image by resizing -> converting to tensor -> normalizing
        """
        img = self.resize_img(image)
        transform = transforms.Compose(
            [
                transforms.ToTensor(),
                transforms.Normalize(mean=IMAGENET_MEAN_1, std=IMAGENET_STD_1),
            ]
        )

        img = torch.as_tensor(transform(img))
        return img.to(self.device).unsqueeze(0)

    def stylize(self, content_img: Image.Image, style_img=None) -> Image.Image:
        """
        Stylizes content image based on selected style, then postprocess by denormalizing -> rescaling to RGB values
        """
        input_tensor = self.preprocess(content_img)

        with torch.no_grad():
            output = self.model(input_tensor).to("cpu").numpy()[0]
            mean = IMAGENET_MEAN_1.reshape(-1, 1, 1)
            std = IMAGENET_STD_1.reshape(-1, 1, 1)
            output = (output * std) + mean  # de-normalize
            output = (np.clip(output, 0.0, 1.0) * 255).astype(np.uint8)
            output = np.moveaxis(output, 0, 2)

        return Image.fromarray(output)

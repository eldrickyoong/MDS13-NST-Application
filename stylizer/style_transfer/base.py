# your_app/style_transfer/base.py

import torch
from abc import ABC, abstractmethod

class BaseStyleTransferModel(ABC):
    def __init__(self, device='cuda'):
        self.device = device
        self.model = None

    @abstractmethod
    def load_model(self, model_path):
        pass

    @abstractmethod
    def stylize(self, content_img_tensor, style_img_tensor) -> torch.Tensor:
        pass

    def preprocess(self, image):
        return image.to(self.device)

    def postprocess(self, tensor):
        return tensor.cpu().clamp(0, 1)

    def to(self, device):
        self.device = device
        if self.model:
            self.model.to(device)
        return self

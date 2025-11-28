from abc import ABC, abstractmethod
import cv2 as cv
import numpy as np
import torch
from PIL.Image import Image

NEW_WIDTH = 1024  # Resize images to this size


class BaseStyleTransferModel(ABC):
    """
    Base class inherited by Johnson and Linear models
    """

    def __init__(self, device="cuda"):
        self.device = device
        self.model = None

    @staticmethod
    def safe_load_wrapper(func):
        """Decorator: catches missing weight files and surfaces clear errors."""

        def wrapper(self, model_path):
            try:
                return func(self, model_path)
            except FileNotFoundError as e:
                raise FileNotFoundError(
                    f"[Error] Missing required file:\n{str(e)}\n\n"
                    f"Ensure all weights are placed in: "
                    f"'repo/stylizer/style_engine/backends/weights/'\n"
                    f"See more at: https://github.com/eldrickyoong/MDS13-NST-Application/releases/tag/v1.0.0"
                )

        return wrapper

    def resize_img(self, image: Image):
        """
        Resizes image such that new width = NEW_WIDTH, and retains original ratio
        """
        img = np.array(image)
        current_height, current_width = img.shape[:2]
        new_height = int(current_height * (NEW_WIDTH / current_width))
        img = cv.resize(img, (NEW_WIDTH, new_height), interpolation=cv.INTER_CUBIC)
        return img

    @abstractmethod
    def load_model(self, model_path):
        pass

    @abstractmethod
    def preprocess(self, image) -> torch.Tensor:
        pass

    @abstractmethod
    def stylize(self, content_img, style_img) -> Image:
        pass

    def postprocess(self, tensor):
        return tensor.cpu().clamp(0, 1)

    def to(self, device):
        self.device = device
        if self.model:
            self.model.to(device)
        return self

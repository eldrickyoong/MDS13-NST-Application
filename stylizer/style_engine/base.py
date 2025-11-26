from abc import ABC, abstractmethod
import cv2 as cv
import numpy as np

NEW_WIDTH = 1280

class BaseStyleTransferModel(ABC):
    def __init__(self, device="cuda"):
        self.device = device
        self.model = None

    @abstractmethod
    def load_model(self, model_path):
        pass

    @abstractmethod
    def stylize(self, content_img_tensor, style_img_tensor):
        pass

    def preprocess(self, image):
        img = np.array(image)
        current_height, current_width = img.shape[:2]
        new_height = int(current_height * (NEW_WIDTH / current_width))
        img = cv.resize(img, (NEW_WIDTH, new_height),
                        interpolation=cv.INTER_CUBIC)
        return img

    def postprocess(self, tensor):
        return tensor.cpu().clamp(0, 1)

    def to(self, device):
        self.device = device
        if self.model:
            self.model.to(device)
        return self

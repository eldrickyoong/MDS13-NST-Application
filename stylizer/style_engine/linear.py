"""
This module includes code adapted from external open-source repositories.
See `README.md` (Acknowledgement section) for full details.
"""

from PIL import Image
import torch
import torchvision.transforms as transforms
from style_engine.backends.linear_style.models import encoder4, decoder4
from style_engine.backends.linear_style.Matrix import MulLayer
from .base import BaseStyleTransferModel


class LinearStyleTransferModel(BaseStyleTransferModel):
    """
    Class used for stylization via Linear Transformation Network, inherites BaseStyleTransferModel
    """

    @BaseStyleTransferModel.safe_load_wrapper
    def load_model(self, model_path):
        self.config = dict()
        self.config["vgg_dir"] = model_path / "vgg_r41.pth"  # pre-trained encoder path
        self.config["decoder_dir"] = (
            model_path / "dec_r41.pth"
        )  # pre-trained decoder path
        self.config["matrixPath"] = model_path / "r41.pth"  # pre-trained model path
        self.config["batchSize"] = 1  # batch size
        self.config["layer"] = "r41"  # features to transfer

        self.vgg = encoder4()
        self.dec = decoder4()

        self.matrix = MulLayer(self.config["layer"])
        self.vgg.load_state_dict(
            torch.load(self.config["vgg_dir"], map_location=self.device)
        )
        self.dec.load_state_dict(
            torch.load(self.config["decoder_dir"], map_location=self.device)
        )
        self.matrix.load_state_dict(
            torch.load(self.config["matrixPath"], map_location=self.device)
        )

        self.vgg.to(self.device)
        self.dec.to(self.device)
        self.matrix.to(self.device)

    def preprocess(self, image: Image.Image) -> torch.Tensor:
        """
        Preprocessing is simply resizing image, no need for normalizing
        """
        img = self.resize_img(image)
        output = transforms.ToTensor()(img).unsqueeze(0).to(self.device)

        return output

    def stylize(self, content_img: Image.Image, style_img: Image.Image):
        """
        Takes in preprocessed content and style image as input, then performs a forward pass for stylization
        """
        with torch.no_grad():
            self.vgg.eval()
            self.dec.eval()
            self.matrix.eval()
            sF = self.vgg(self.preprocess(style_img))
            cF = self.vgg(self.preprocess(content_img))

            feature, transmatrix = self.matrix(
                cF[self.config["layer"]], sF[self.config["layer"]]
            )

            output = self.dec(feature)
            return self.postprocess(output.squeeze(0))

    def postprocess(self, tensor):
        tensor = tensor.detach().squeeze(0).clamp(0, 1)
        return transforms.ToPILImage()(tensor.cpu())

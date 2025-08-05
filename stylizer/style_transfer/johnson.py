import torch
from style_transfer.johnson_fast_style.transformer_net import TransformerNet
from .base import BaseStyleTransferModel

class JohnsonStyleTransferModel(BaseStyleTransferModel):
    def load_model(self, model_path):
      if model_path is None:
        raise ValueError("model_path is required for Johnson model.")
      self.model = TransformerNet().to(self.device)
      state = torch.load(model_path, map_location=self.device)
      self.model.load_state_dict(state["state_dict"])
      self.model.eval()

    def stylize(self, content_img_tensor, style_img_tensor=None):
        with torch.no_grad():
            input_tensor = self.preprocess(content_img_tensor)
            output = self.model(input_tensor)
            return self.postprocess(output.squeeze(0))
import torch
from .base import BaseStyleTransferModel
from torchvision import transforms
from torch.autograd import Variable
from style_transfer.gatys_iterative_style.vgg_nets import Vgg19
from torch.optim import LBFGS
from PIL import Image
import numpy as np

IMAGENET_MEAN_255 = [123.675, 116.28, 103.53]
IMAGENET_STD_NEUTRAL = [1, 1, 1]

class GatysStyleTransferModel(BaseStyleTransferModel):
    def preprocess(self, image):
        transform = transforms.Compose([
            transforms.Lambda(lambda x: x.mul(255)),
            transforms.Normalize(mean=IMAGENET_MEAN_255, std=IMAGENET_STD_NEUTRAL)
        ])
        
        image = transform(image)
        
        return super().preprocess(image)
    
    def load_model(self, model_path):
        self.config = dict()
        self.config['content_weight'] = 1e5
        self.config['style_weight'] = 3e4
        self.config['tv_weight'] = 1e0
        self.config['num_iterations'] = 1000
        
        model = Vgg19(requires_grad=False, show_progress=True)
        layer_names = model.layer_names
        content_feature_maps_index = model.content_feature_maps_index
        style_feature_maps_indices = model.style_feature_maps_indices
        
        self.content_feature_maps_index_name = (content_feature_maps_index, layer_names[content_feature_maps_index])
        self.style_feature_maps_indices_names = (style_feature_maps_indices, layer_names)
        
        self.model = model.to(self.device).eval()

    def stylize(self, content_img_tensor, style_img_tensor):
        content_img_tensor = self.preprocess(content_img_tensor)
        style_img_tensor = self.preprocess(style_img_tensor)
        self.optimizing_img = Variable(content_img_tensor, requires_grad=True)
        
        # Load model and target features
        content_img_set_of_feature_maps = self.model(content_img_tensor)
        style_img_set_of_feature_maps = self.model(style_img_tensor)
        
        self.target_content_representation = content_img_set_of_feature_maps[self.content_feature_maps_index_name[0]].squeeze(0)
        self.target_style_representation = [self._gram_matrix(x) for cnt, x in enumerate(style_img_set_of_feature_maps) if cnt in self.style_feature_maps_indices_names[0]]
        
        self.optimizer = LBFGS((self.optimizing_img,), max_iter=self.config["num_iterations"], line_search_fn='strong_wolfe')
        self.cnt = 0
        
        self.optimizer.step(self._closure)
        
        out_tensor = self.optimizing_img.detach().cpu().squeeze(0).clone()  # shape: (3, H, W)
        for c, mean in enumerate(IMAGENET_MEAN_255):
            out_tensor[c] += mean
        out_tensor = out_tensor.clamp(0, 255).unsqueeze(0)
        
        return out_tensor / 255.0
        
    def _gram_matrix(self, x, should_normalize=True):
        (b, ch, h, w) = x.size()
        features = x.view(b, ch, w * h)
        features_t = features.transpose(1, 2)
        gram = features.bmm(features_t)
        if should_normalize:
            gram /= ch * h * w
        return gram
    
    def _total_variation(self, y):
        return torch.sum(torch.abs(y[:, :, :, :-1] - y[:, :, :, 1:])) + \
            torch.sum(torch.abs(y[:, :, :-1, :] - y[:, :, 1:, :]))
    
    def _build_loss(self):
        current_set_of_feature_maps = self.model(self.optimizing_img)
        current_content_representation = current_set_of_feature_maps[self.content_feature_maps_index_name[0]].squeeze(axis=0)
        content_loss = torch.nn.MSELoss(reduction='mean')(self.target_content_representation, current_content_representation)

        style_loss = 0.0
        current_style_representation = [self._gram_matrix(x) for cnt, x in enumerate(current_set_of_feature_maps) if cnt in self.style_feature_maps_indices_names[0]]
        for gram_gt, gram_hat in zip(self.target_style_representation, current_style_representation):
            style_loss += torch.nn.MSELoss(reduction='sum')(gram_gt[0], gram_hat[0])
        style_loss /= len(self.target_style_representation)
        
        tv_loss = self._total_variation(self.optimizing_img)
        total_loss = self.config['content_weight'] * content_loss + self.config['style_weight'] * style_loss + self.config['tv_weight'] * tv_loss
        
        return total_loss, content_loss, style_loss, tv_loss
        
    def _closure(self):
        if torch.is_grad_enabled():
            self.optimizer.zero_grad()
        total_loss, content_loss, style_loss, tv_loss = self._build_loss()
        if total_loss.requires_grad:
            total_loss.backward()
        with torch.no_grad():
            print(f'L-BFGS | iteration: {self.cnt:03}, total loss={total_loss.item():12.4f}, content_loss={self.config["content_weight"] * content_loss.item():12.4f}, style loss={self.config["style_weight"] * style_loss.item():12.4f}, tv loss={self.config["tv_weight"] * tv_loss.item():12.4f}')
        
        self.cnt += 1
        return total_loss
        
        
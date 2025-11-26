import torch
import torchvision.transforms as transforms
from style_engine.backends.linear_style.models import encoder4, decoder4
from style_engine.backends.linear_style.Matrix import MulLayer
from .base import BaseStyleTransferModel

class LinearStyleTransferModel(BaseStyleTransferModel):
    
    def load_model(self, model_path):
        self.config = dict()
        self.config['vgg_dir'] = model_path / 'vgg_r41.pth' # pre-trained encoder path
        self.config['decoder_dir'] = model_path / 'dec_r41.pth' # pre-trained decoder path
        self.config['matrixPath'] = model_path / 'r41.pth' # pre-trained model path
        self.config['batchSize'] = 1 # batch size
        self.config['layer'] = 'r41' # which features to transfer, either r31 or r41
        
        self.vgg = encoder4()
        self.dec = decoder4()
        
        self.matrix = MulLayer(self.config['layer'])
        self.vgg.load_state_dict(torch.load(self.config['vgg_dir'], map_location=self.device))
        self.dec.load_state_dict(torch.load(self.config['decoder_dir'], map_location=self.device))
        self.matrix.load_state_dict(torch.load(self.config['matrixPath'], map_location=self.device))
        
        self.vgg.to(self.device)
        self.dec.to(self.device)
        self.matrix.to(self.device)
    
    def preprocess(self, image):
        
        img = super().preprocess(image)
        transform = transforms.Compose([
            transforms.ToTensor()
        ])
        
        return transform(img).unsqueeze(0).to(self.device)

    def stylize(self, content_img_tensor, style_img_tensor):
        
        with torch.no_grad():
            self.vgg.eval()
            self.dec.eval()
            self.matrix.eval()
            sF = self.vgg(self.preprocess(style_img_tensor))
            cF = self.vgg(self.preprocess(content_img_tensor))
            
            if self.config['layer'] == 'r41':
                feature, transmatrix = self.matrix(cF[self.config['layer']], sF[self.config['layer']])
            else:
                feature, transmatrix = self.matrix(cF, sF)

            output = self.dec(feature)
            return self.postprocess(output.squeeze(0))
    
    def postprocess(self, tensor):
        tensor = tensor.detach().squeeze(0).clamp(0, 1)
        return transforms.ToPILImage()(tensor.cpu())
          
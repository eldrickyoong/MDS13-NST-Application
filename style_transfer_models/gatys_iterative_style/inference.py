from PIL import Image
import torch
from torch.optim import Adam, LBFGS
from torch.autograd import Variable
import numpy as np
import shared.state as state
from torchvision.transforms.functional import to_pil_image


from .utils import prepare_img_from_pil, prepare_model, gram_matrix, total_variation

def build_loss(neural_net, optimizing_img, target_representations, content_feature_maps_index, style_feature_maps_indices, config):
    target_content_representation = target_representations[0]
    target_style_representation = target_representations[1]

    current_set_of_feature_maps = neural_net(optimizing_img)

    current_content_representation = current_set_of_feature_maps[content_feature_maps_index].squeeze(axis=0)
    content_loss = torch.nn.MSELoss(reduction='mean')(target_content_representation, current_content_representation)

    style_loss = 0.0
    current_style_representation = [gram_matrix(x) for cnt, x in enumerate(current_set_of_feature_maps) if cnt in style_feature_maps_indices]
    for gram_gt, gram_hat in zip(target_style_representation, current_style_representation):
        style_loss += torch.nn.MSELoss(reduction='sum')(gram_gt[0], gram_hat[0])
    style_loss /= len(target_style_representation)

    tv_loss = total_variation(optimizing_img)

    total_loss = config['content_weight'] * content_loss + config['style_weight'] * style_loss + config['tv_weight'] * tv_loss

    return total_loss, content_loss, style_loss, tv_loss

def make_tuning_step(neural_net, optimizer, target_representations, content_feature_maps_index, style_feature_maps_indices, config):
    # Builds function that performs a step in the tuning loop
    def tuning_step(optimizing_img):
        total_loss, content_loss, style_loss, tv_loss = build_loss(neural_net, optimizing_img, target_representations, content_feature_maps_index, style_feature_maps_indices, config)
        # Computes gradients
        total_loss.backward()
        # Updates parameters and zeroes gradients
        optimizer.step()
        optimizer.zero_grad()
        return total_loss, content_loss, style_loss, tv_loss

    # Returns the function that will be called inside the tuning loop
    return tuning_step

def tensor_to_pil(tensor):
    # Assumes tensor shape is (1, 3, H, W)
    tensor = tensor.detach().cpu().squeeze(0)
    return to_pil_image(tensor.clamp(0, 1))

def neural_style_transfer_from_pil(content_img: Image.Image, style_img: Image.Image, config: dict) -> Image.Image:

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Prepare input tensors
    content_tensor = prepare_img_from_pil(content_img, config['height'], device)
    style_tensor = prepare_img_from_pil(style_img, config['height'], device)

    # Initialization
    if config['init_method'] == 'random':
        init_tensor = torch.from_numpy(np.random.normal(0, 90, content_tensor.shape).astype(np.float32)).to(device)
    elif config['init_method'] == 'style':
        init_tensor = prepare_img_from_pil(style_img, content_tensor.shape[2:], device)
    else:
        init_tensor = content_tensor

    optimizing_img = Variable(init_tensor, requires_grad=True)

    # Load model and target features
    neural_net, content_feature_maps_index_name, style_feature_maps_indices_names = prepare_model(config['model'], device)
    content_img_set_of_feature_maps = neural_net(content_tensor)
    style_img_set_of_feature_maps = neural_net(style_tensor)

    target_content_representation = content_img_set_of_feature_maps[content_feature_maps_index_name[0]].squeeze(axis=0)
    target_style_representation = [gram_matrix(x) for cnt, x in enumerate(style_img_set_of_feature_maps) if cnt in style_feature_maps_indices_names[0]]
    target_representations = [target_content_representation, target_style_representation]

    # Optimization
    num_iters = {"lbfgs": 1000, "adam": 3000}
    if config['optimizer'] == 'adam':
        optimizer = Adam([optimizing_img], lr=10)
        step = make_tuning_step(model, optimizer, target_representations, content_idx[0], style_indices[0], config)
        for _ in range(num_iters['adam']):
            step(optimizing_img)
    else:
        optimizer = LBFGS((optimizing_img,), max_iter=num_iters['lbfgs'], line_search_fn='strong_wolfe')
        cnt = 0

        def closure():
            nonlocal cnt
            if torch.is_grad_enabled():
                optimizer.zero_grad()
            total_loss, content_loss, style_loss, tv_loss = build_loss(neural_net, optimizing_img, target_representations, content_feature_maps_index_name[0], style_feature_maps_indices_names[0], config)
            if total_loss.requires_grad:
                total_loss.backward()
            with torch.no_grad():
                print(f'L-BFGS | iteration: {cnt:03}, total loss={total_loss.item():12.4f}, content_loss={config["content_weight"] * content_loss.item():12.4f}, style loss={config["style_weight"] * style_loss.item():12.4f}, tv loss={config["tv_weight"] * tv_loss.item():12.4f}')
            
            cnt += 1
            return total_loss
        
        optimizer.step(closure)


    # Convert result to PIL
    final_tensor = optimizing_img.detach().cpu().squeeze(0).clamp(0, 1)
    final_np = final_tensor.permute(1, 2, 0).numpy() * 255
    return Image.fromarray(final_np.astype("uint8"))

if __name__ == "__main__":
    gatys_config = {
    "height": 400,
    "content_weight": 1e5,
    "style_weight": 3e4,
    "tv_weight": 1e0,
    "optimizer": "lbfgs",
    "model": "vgg19",
    "init_method": "content",
    }
    content_path = r'C:\Users\eldri\My Drive\Monash\Y3S2\FIT3164\MDS13-NST-Application\static\images\content-images\figures.jpg'
    style_path = r'C:\Users\eldri\My Drive\Monash\Y3S2\FIT3164\MDS13-NST-Application\static\images\gatys_iterative_style\ben_giles.jpg'
    
    content_img = Image.open(content_path).convert("RGB")
    style_img = Image.open(content_path).convert("RGB")
    result_img = neural_style_transfer_from_pil(content_img, style_img, gatys_config)

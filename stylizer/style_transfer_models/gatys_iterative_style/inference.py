from PIL import Image
import torch
from torch.optim import Adam, LBFGS
from torch.autograd import Variable
import numpy as np
from torchvision.transforms.functional import to_pil_image
from pathlib import Path
import matplotlib.pyplot as plt


from .utils import prepare_img, prepare_model, gram_matrix, total_variation, save_and_maybe_display, get_uint8_range

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

def neural_style_transfer(content_img_path: Path, style_img_path: Path, config: dict) -> Image.Image:

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Prepare input tensors
    content_img = prepare_img(content_img_path, config['height'], device)
    style_img = prepare_img(style_img_path, config['height'], device)

    if config['init_method'] == 'random':
        # white_noise_img = np.random.uniform(-90., 90., content_img.shape).astype(np.float32)
        gaussian_noise_img = np.random.normal(loc=0, scale=90., size=content_img.shape).astype(np.float32)
        init_img = torch.from_numpy(gaussian_noise_img).float().to(device)
    elif config['init_method'] == 'content':
        init_img = content_img
    else:
        # init image has same dimension as content image - this is a hard constraint
        # feature maps need to be of same size for content image and init image
        style_img_resized = prepare_img(style_img_path, np.asarray(content_img.shape[2:]), device)
        init_img = style_img_resized

    optimizing_img = Variable(init_img, requires_grad=True)

    # Load model and target features
    neural_net, content_feature_maps_index_name, style_feature_maps_indices_names = prepare_model(config['model'], device)
    content_img_set_of_feature_maps = neural_net(content_img)
    style_img_set_of_feature_maps = neural_net(style_img)

    target_content_representation = content_img_set_of_feature_maps[content_feature_maps_index_name[0]].squeeze(axis=0)
    target_style_representation = [gram_matrix(x) for cnt, x in enumerate(style_img_set_of_feature_maps) if cnt in style_feature_maps_indices_names[0]]
    target_representations = [target_content_representation, target_style_representation]

    # Optimization
    num_of_iterations = {
        "lbfgs": 1000,
        "adam": 3000,
    }
    
    #
    # Start of optimization procedure
    #
    if config['optimizer'] == 'adam':
        optimizer = Adam((optimizing_img,), lr=1e1)
        tuning_step = make_tuning_step(neural_net, optimizer, target_representations, content_feature_maps_index_name[0], style_feature_maps_indices_names[0], config)
        for cnt in range(num_of_iterations[config['optimizer']]):
            total_loss, content_loss, style_loss, tv_loss = tuning_step(optimizing_img)
            with torch.no_grad():
                print(f'Adam | iteration: {cnt:03}, total loss={total_loss.item():12.4f}, content_loss={config["content_weight"] * content_loss.item():12.4f}, style loss={config["style_weight"] * style_loss.item():12.4f}, tv loss={config["tv_weight"] * tv_loss.item():12.4f}')
    else:
        optimizer = LBFGS((optimizing_img,), max_iter=num_of_iterations['lbfgs'], line_search_fn='strong_wolfe')
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
                save_and_maybe_display(optimizing_img, config["output_img_dir"], config, cnt, num_of_iterations[config['optimizer']], should_display=False)
            
            cnt += 1
            return total_loss
        
        optimizer.step(closure)
        
    
    out_img = optimizing_img.squeeze(axis=0).to('cpu').detach().numpy()
    out_img = np.moveaxis(out_img, 0, 2)  # swap channel from 1st to 3rd position: ch, _, _ -> _, _, chr
    plt.imshow(np.uint8(get_uint8_range(out_img)))
    plt.show()
    

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
    "saving_freq": -1,
    "output_img_dir": r"C:\Users\eldri\My Drive\Monash\Y3S2\FIT3164\MDS13-NST-Application\stylizer\transfer\static\images\gatys_iterative_style\check",
    "img_format": (4, '.jpg'),
    "content_img_name": 'figures.jpg',
    "style_img_name": "ben_giles.jpg"
    }
    content_path = Path(r'C:\Users\eldri\My Drive\Monash\Y3S2\FIT3164\MDS13-NST-Application\stylizer\transfer\static\images\content-images\figures.jpg')
    style_path = Path(r'C:\Users\eldri\My Drive\Monash\Y3S2\FIT3164\MDS13-NST-Application\stylizer\transfer\static\images\gatys_iterative_style\ben_giles.jpg')
    
    result_img = neural_style_transfer(content_path, style_path, gatys_config)

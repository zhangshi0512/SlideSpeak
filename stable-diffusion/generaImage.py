import torch
from diffusers import StableDiffusionPipeline, DDIMScheduler
from PIL import Image
import numpy as np

def generaImage(prompt):

    model_path = "./stable-diffusion-model"
    # check if cuda is available
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device is : {device}")

    # stop safety check
    pipe = StableDiffusionPipeline.from_pretrained(
        model_path,
        safety_checker=None,
        requires_safety_checker=False
    )

    # optimization
    pipe.enable_attention_slicing()

    # DDIM
    scheduler = DDIMScheduler.from_pretrained(model_path, subfolder="scheduler")
    pipe.scheduler = scheduler

    # transfer to device
    pipe = pipe.to(device)
    if device == "cuda":
        pipe.to(torch_dtype=torch.float16)

    print("Model will be loaded to:", device)
    print("The accuracy:", pipe.unet.dtype)

    print(f"prompt is : {prompt}")
    print("Start generating image...")

    try:
        # here to modify the quality of picture by increasing/decreasing num_inference_steps (60)
        # also can change guidance_scale (Increase from 7.5 to 8.0-15.0)
        # Increase resolution 768
        # and seeds
        image = pipe(
            prompt=prompt,
            guidance_scale=7.5,
            num_inference_steps=30,
            height=512,
            width=512,
        ).images[0]

        # pic check
        img_array = np.array(image)
        print("Pic information:")
        print(f"shape: {img_array.shape}")
        print(f"data type: {img_array.dtype}")
        print(f"min: {img_array.min()}, max: {img_array.max()}, mean: {img_array.mean()}")

        # check NaN
        if np.isnan(img_array).any():
            print("WARNING: it contains NaN!")

        # check if all black
        if img_array.max() < 10:
            print("WARNING: all black")
        else:
            print("Successful!")

        # save pic
        output_path = "generated_image.png"
        image.save(output_path)
        print(f"Pic has been saved to: {output_path}")

    except Exception as e:
        print(f"An error : {e}")

key_words = "cyberpunk future city with neon lights, high quality photograph"
generaImage(key_words)

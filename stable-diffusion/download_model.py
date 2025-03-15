from huggingface_hub import snapshot_download

# Replace with the model you want
model_id = "stabilityai/stable-diffusion-2-1"

# Download the model to a local directory
snapshot_download(repo_id=model_id, local_dir="./stable-diffusion-model")

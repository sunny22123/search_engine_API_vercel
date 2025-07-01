import torch
import open_clip
from PIL import Image
import numpy as np

class OpenCLIPEmbedder:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            'ViT-B-32', pretrained='laion2b_s34b_b79k'
        )
        self.model = self.model.to(self.device)
        self.tokenizer = open_clip.get_tokenizer('ViT-B-32')

    def get_image_embedding(self, image: Image.Image) -> np.ndarray:
        image_tensor = self.preprocess(image).unsqueeze(0).to(self.device)
        with torch.no_grad():
            embedding = self.model.encode_image(image_tensor).squeeze().cpu().numpy()
        normalized_embedding = embedding / np.linalg.norm(embedding)
        return normalized_embedding

    def get_batch_embeddings(self, images: list[Image.Image]) -> np.ndarray:
        image_tensors = torch.stack([self.preprocess(img) for img in images]).to(self.device)
        with torch.no_grad():
            embeddings = self.model.encode_image(image_tensors).cpu().numpy()
        normalized_embeddings = embeddings / np.linalg.norm(embeddings, axis=1)[:, None]
        return normalized_embeddings

    def get_text_embedding(self, text: str) -> np.ndarray:
        tokens = self.tokenizer([text])
        tokens = torch.tensor(tokens).to(self.device)
        with torch.no_grad():
            text_features = self.model.encode_text(tokens).squeeze().cpu().numpy()
        normalized_embedding = text_features / np.linalg.norm(text_features)
        return normalized_embedding

clip_embedder = OpenCLIPEmbedder() 
import base64
import os

from openai import OpenAI


class ImageGenerator:
    """Reusable OpenAI image generation service."""

    DEFAULT_MODEL = "gpt-image-1"

    def __init__(self, model: str | None = None) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set.")

        self.client = OpenAI(api_key=api_key)
        self.model = model or self.DEFAULT_MODEL

    def generate_image(self, prompt: str) -> bytes:
        response = self.client.images.generate(model=self.model, prompt=prompt)
        image_base64 = response.data[0].b64_json
        if not image_base64:
            raise ValueError("Image generation returned empty image data.")
        return base64.b64decode(image_base64)

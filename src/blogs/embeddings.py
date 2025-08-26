import os
from google import genai
from typing import List
from google.genai import types
import numpy as np
from django.conf import settings

os.environ['GEMINI_API_KEY'] = settings.GEMINI_API_KEY

client = genai.Client()

def generate_embeddings(text: List[str]) -> List[int]:
    response = client.models.embed_content(
        model='gemini-embedding-001',
        contents=text,
        config=types.EmbedContentConfig(output_dimensionality=768)
    )

    return np.array([embedding.values for embedding in response.embeddings][0])


if __name__ == "__main__":
    print(generate_embeddings("today is a wonderful day"))

from __future__ import annotations

import hashlib
from typing import List

try:
    from sentence_transformers import SentenceTransformer
except Exception:  # pragma: no cover
    SentenceTransformer = None


class EmbeddingService:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        self.model_name = model_name
        self.model = None

    def embed(self, text: str) -> List[float]:
        digest = hashlib.sha256(text.lower().encode("utf-8")).digest()
        return [float(value) / 255.0 for value in digest[:64]] + [0.0] * 288

    def embed_many(self, texts: List[str]) -> List[List[float]]:
        return [self.embed(text) for text in texts]

from __future__ import annotations

from typing import List


def chunk_text(text: str, chunk_size: int = 400, overlap: int = 80) -> List[str]:
    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = max(0, end - overlap)
    return chunks

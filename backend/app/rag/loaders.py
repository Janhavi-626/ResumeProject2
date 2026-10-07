from __future__ import annotations

from pathlib import Path
from typing import List


class DocumentLoader:
    def __init__(self, base_dir: str | Path) -> None:
        self.base_dir = Path(base_dir)

    def load_documents(self) -> List[dict]:
        documents: List[dict] = []
        if not self.base_dir.exists():
            return documents

        for file_path in sorted(self.base_dir.rglob("*.txt")):
            text = file_path.read_text(encoding="utf-8")
            documents.append({
                "document_id": file_path.stem,
                "title": file_path.stem.replace("_", " ").title(),
                "source": str(file_path),
                "content": text,
                "category": "policy",
                "version": "v1.0",
                "effective_date": "2026-01-01",
            })
        return documents

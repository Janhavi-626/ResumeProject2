from __future__ import annotations

from pathlib import Path

from app.rag.retriever import KnowledgeRetriever


def ingest() -> None:
    base_dir = Path(__file__).resolve().parents[1] / "knowledge_base"
    retriever = KnowledgeRetriever(str(base_dir))
    retriever.ingest()
    print(f"Ingested knowledge from {base_dir}")


if __name__ == "__main__":
    ingest()

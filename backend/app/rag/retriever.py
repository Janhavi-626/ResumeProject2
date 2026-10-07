from __future__ import annotations

from typing import Any, Dict, List

from app.rag.loaders import DocumentLoader
from app.rag.chunking import chunk_text
from app.rag.embeddings import EmbeddingService
from app.rag.vector_store import ChromaVectorStore


class KnowledgeRetriever:
    def __init__(self, base_dir: str, persist_directory: str | None = None) -> None:
        self.loader = DocumentLoader(base_dir)
        self.embedding_service = EmbeddingService()
        self.vector_store = ChromaVectorStore(persist_directory)

    def ingest(self) -> int:
        docs = self.loader.load_documents()
        records = []
        for document in docs:
            chunks = chunk_text(document["content"])
            for idx, chunk in enumerate(chunks):
                records.append({
                    "id": f"{document['document_id']}-{idx}",
                    "text": chunk,
                    "embedding": self.embedding_service.embed(chunk),
                    "metadata": {
                        "document_id": document["document_id"],
                        "title": document["title"],
                        "source": document["source"],
                        "category": document["category"],
                        "version": document["version"],
                        "effective_date": document["effective_date"],
                    },
                })
        self.vector_store.add_documents(records)
        return len(records)

    def search(self, query: str, k: int = 3, filters: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
        return self.vector_store.search(
            query,
            k=k,
            filters=filters,
            embedding=[self.embedding_service.embed(query)],
        )

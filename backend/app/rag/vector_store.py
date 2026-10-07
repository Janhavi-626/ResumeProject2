from __future__ import annotations

import os
from typing import Any, Dict, List

import chromadb


class ChromaVectorStore:
    def __init__(self, persist_directory: str | None = None) -> None:
        self.persist_directory = persist_directory or os.getenv("CHROMA_PERSIST_DIRECTORY", "./backend/.chroma")
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        self.collection = self.client.get_or_create_collection(name="return_policies")

    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        if not documents:
            return
        ids = [doc["id"] for doc in documents]
        texts = [doc["text"] for doc in documents]
        metadatas = [doc.get("metadata", {}) for doc in documents]
        embeddings = [doc.get("embedding") for doc in documents]
        if any(not embedding for embedding in embeddings):
            embeddings = [[0.0] * 384 for _ in texts]

        self.collection.upsert(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)

    def search(self, query: str, k: int = 5, filters: Dict[str, Any] | None = None, embedding: List[List[float]] | None = None) -> List[Dict[str, Any]]:
        query_embedding = embedding or [[0.0] * 320]
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=k,
            where=filters,
        )
        hits = []
        for doc, meta, dist in zip(results.get("documents", [[]])[0], results.get("metadatas", [[]])[0], results.get("distances", [[]])[0]):
            hits.append({"content": doc, "metadata": meta, "distance": dist})
        return hits

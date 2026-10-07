from __future__ import annotations

from typing import Any, Dict

from app.rag.retriever import KnowledgeRetriever
from app.tools.api_tools import get_customer, get_delivery_information, get_order, get_product
from app.tools.database_tools import fetch_case_history, fetch_customer_history, fetch_return_request


class RetrievalAgent:
    def __init__(self, knowledge_retriever: KnowledgeRetriever | None = None) -> None:
        self.name = "retrieval"
        self.knowledge_retriever = knowledge_retriever

    def run(self, source_data: Dict[str, Any]) -> Dict[str, Any]:
        customer_id = source_data.get("customer_id") or "CUS-016"
        order_id = source_data.get("order_id") or "ORD-889"
        product_id = source_data.get("product_id") or "PRD-1234"
        return_id = source_data.get("return_id") or "RET-102"
        policy_query = "damaged electronics return policy fraud review escalation"
        policy_documents = self.knowledge_retriever.search(policy_query, k=3) if self.knowledge_retriever else []
        policy_documents = [
            {
                "document_id": result["metadata"]["document_id"],
                "title": result["metadata"]["title"],
                "source": result["metadata"]["source"],
                "section": result["content"],
                "page": None,
                "version": result["metadata"]["version"],
                "effective_date": result["metadata"]["effective_date"],
                "excerpt": result["content"],
                "citation": f"{result['metadata']['document_id']} §{result['metadata']['category']}",
            }
            for result in policy_documents
        ]

        return {
            "customer": get_customer(customer_id),
            "order": get_order(order_id),
            "product": get_product(product_id),
            "delivery": get_delivery_information(order_id),
            "return_request": fetch_return_request(return_id),
            "customer_history": fetch_customer_history(customer_id),
            "case_history": fetch_case_history(order_id),
            "policy_documents": policy_documents,
        }

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, TypedDict
from uuid import uuid4

from langgraph.graph import END, START, StateGraph

from app.graph.nodes import GraphNodes
from app.rag.retriever import KnowledgeRetriever


class ReturnWorkflowState(TypedDict, total=False):
    workflow_id: str
    session_id: str
    user_query: str
    conversation_history: list[dict[str, str]]
    retry_count: int
    intent: str
    entities: dict[str, Any]
    retrieved_data: dict[str, Any]
    ml_prediction: dict[str, Any]
    investigation_result: dict[str, Any]
    validation_result: dict[str, Any]
    proposed_actions: list[str]
    final_response: str
    confidence: float
    customer_id: str | None
    order_id: str | None
    product_id: str | None
    return_id: str | None
    workflow_status: str
    human_approval: str | None


class ReturnWorkflow:
    def __init__(self, knowledge_retriever=None) -> None:
        if knowledge_retriever is None:
            knowledge_root = Path(__file__).resolve().parents[2] / "knowledge_base"
            knowledge_retriever = KnowledgeRetriever(str(knowledge_root), persist_directory="backend/.chroma")
        self.nodes = GraphNodes(knowledge_retriever)
        self.graph = self._build_graph()

    def _build_graph(self):
        builder = StateGraph(ReturnWorkflowState)
        builder.add_node("triage", self.nodes.run_triage)
        builder.add_node("retrieval", self.nodes.run_retrieval)
        builder.add_node("classification", self.nodes.run_classification)
        builder.add_node("investigation", self.nodes.run_investigation)
        builder.add_node("validation", self.nodes.run_validation)
        builder.add_node("approval", self.nodes.run_approval)
        builder.add_node("action", self.nodes.run_action)
        builder.add_node("response", self.nodes.run_response)

        builder.add_edge(START, "triage")
        builder.add_edge("triage", "retrieval")
        builder.add_edge("retrieval", "classification")
        builder.add_edge("classification", "investigation")
        builder.add_edge("investigation", "validation")
        builder.add_conditional_edges(
            "validation",
            lambda state: (
                "approval"
                if state.get("validation_result", {}).get("requires_human_review")
                else "action"
                if state.get("validation_result", {}).get("status") != "BLOCK"
                else END
            ),
            {"approval": "approval", "action": "action", END: END},
        )
        builder.add_edge("approval", END)
        builder.add_edge("action", "response")
        builder.add_edge("response", END)
        return builder.compile()

    def run(self, user_query: str, session_id: str = "session-1", workflow_id: str | None = None) -> Dict[str, Any]:
        workflow_id = workflow_id or f"WF-{uuid4().hex[:10].upper()}"
        initial_state: ReturnWorkflowState = {
            "workflow_id": workflow_id,
            "session_id": session_id,
            "user_query": user_query,
            "conversation_history": [{"role": "user", "content": user_query}],
            "retry_count": 0,
            "confidence": 0.0,
            "workflow_status": "RUNNING",
        }
        result = self.graph.invoke(initial_state)
        return dict(result)

    def resume_approval(self, state: Dict[str, Any], action: str) -> Dict[str, Any]:
        if action not in {"approve", "reject"}:
            raise ValueError("Approval must be approve or reject")
        state = dict(state)
        state["human_approval"] = action
        state["workflow_status"] = "RESOLVED" if action == "approve" else "REJECTED"
        if action == "approve":
            state = self.nodes.run_action(state)
            state = self.nodes.run_response(state)
        return state

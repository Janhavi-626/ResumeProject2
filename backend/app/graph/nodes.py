from __future__ import annotations

from typing import Any, Dict

from app.agents.action import ActionAgent
from app.agents.classification import ClassificationAgent
from app.agents.investigation import InvestigationAgent
from app.agents.retrieval import RetrievalAgent
from app.agents.response import ResponseAgent
from app.agents.supervisor import SupervisorAgent
from app.agents.triage import TriageAgent
from app.agents.validator import ValidationAgent
from app.rag.retriever import KnowledgeRetriever


class GraphNodes:
    def __init__(self, knowledge_retriever: KnowledgeRetriever | None = None) -> None:
        self.supervisor = SupervisorAgent()
        self.triage = TriageAgent()
        self.retrieval = RetrievalAgent(knowledge_retriever)
        self.classification = ClassificationAgent()
        self.investigation = InvestigationAgent()
        self.action = ActionAgent()
        self.validator = ValidationAgent()
        self.response = ResponseAgent()

    def run_triage(self, state: Dict[str, Any]) -> Dict[str, Any]:
        triage_context = {key: value for key, value in state.items() if key != "user_query"}
        triage_result = self.triage.run(state["user_query"], **triage_context)
        state["intent"] = triage_result.intent
        state["entities"] = triage_result.entities
        state["confidence"] = triage_result.confidence
        state["return_id"] = triage_result.entities.get("return_id")
        state["customer_id"] = triage_result.entities.get("customer_id")
        state["order_id"] = triage_result.entities.get("order_id")
        state["product_id"] = triage_result.entities.get("product_id")
        return state

    def run_retrieval(self, state: Dict[str, Any]) -> Dict[str, Any]:
        state["retrieved_data"] = self.retrieval.run({
            "customer_id": state.get("customer_id"),
            "order_id": state.get("order_id"),
            "product_id": state.get("product_id"),
            "return_id": state.get("return_id"),
        })
        return state

    def run_classification(self, state: Dict[str, Any]) -> Dict[str, Any]:
        payload = state.get("retrieved_data", {}).get("return_request", {})
        result = self.classification.run(payload)
        state["ml_prediction"] = result
        state["prediction_probability"] = result["probability"]
        state["reason_codes"] = result["reason_codes"]
        return state

    def run_investigation(self, state: Dict[str, Any]) -> Dict[str, Any]:
        payload = {**state.get("retrieved_data", {}).get("return_request", {}), **state.get("ml_prediction", {})}
        state["investigation_result"] = self.investigation.run(payload, state.get("retrieved_data", {}).get("policy_documents", [])).model_dump()
        return state

    def run_action(self, state: Dict[str, Any]) -> Dict[str, Any]:
        classification_name = state.get("ml_prediction", {}).get("predicted_class", "STANDARD_RETURN")
        result = self.action.run(classification_name, state.get("workflow_id", "WF-000"), state.get("validation_result", {}).get("requires_human_review", False))
        state["proposed_actions"] = result.get("actions", [])
        return state

    def run_validation(self, state: Dict[str, Any]) -> Dict[str, Any]:
        validation = self.validator.run(state.get("ml_prediction", {}), state.get("investigation_result", {}), state.get("retrieved_data", {}).get("policy_documents", []))
        state["validation_result"] = validation.model_dump()
        return state

    def run_approval(self, state: Dict[str, Any]) -> Dict[str, Any]:
        state["workflow_status"] = "PENDING_HUMAN_REVIEW"
        state["human_approval"] = None
        return state

    def run_response(self, state: Dict[str, Any]) -> Dict[str, Any]:
        triage = {"intent": state.get("intent", "return_investigation"), "recommended_route": "inspection"}
        response = self.response.run(
            triage,
            state.get("ml_prediction", {}),
            state.get("investigation_result", {}),
            state.get("validation_result", {}),
            state.get("retrieved_data", {}).get("policy_documents", []),
        )
        state["final_response"] = response
        state["workflow_status"] = "RESOLVED"
        return state

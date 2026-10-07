from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AgentState(BaseModel):
    session_id: str
    user_id: Optional[str] = None
    user_query: str
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)
    return_id: Optional[str] = None
    customer_id: Optional[str] = None
    order_id: Optional[str] = None
    product_id: Optional[str] = None
    intent: Optional[str] = None
    entities: Dict[str, Any] = Field(default_factory=dict)
    retrieved_data: Dict[str, Any] = Field(default_factory=dict)
    retrieved_documents: List[Dict[str, Any]] = Field(default_factory=list)
    ml_prediction: Optional[Dict[str, Any]] = None
    prediction_probability: float = 0.0
    reason_codes: List[str] = Field(default_factory=list)
    investigation_result: Optional[Dict[str, Any]] = None
    proposed_actions: List[str] = Field(default_factory=list)
    tool_results: List[Dict[str, Any]] = Field(default_factory=list)
    confidence: float = 0.0
    validation_result: Optional[Dict[str, Any]] = None
    human_approval: Optional[str] = None
    errors: List[str] = Field(default_factory=list)
    final_response: Optional[str] = None

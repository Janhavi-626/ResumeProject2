from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


ReturnCategory = Literal["STANDARD_RETURN", "POLICY_EXCEPTION", "FRAUD_REVIEW", "SPECIALIST_ASSESSMENT"]
ValidationStatus = Literal["PASS", "RETRY", "HUMAN_REVIEW", "BLOCK"]
ProbabilityBand = Literal["LOW", "MEDIUM", "HIGH"]


class TriageInput(BaseModel):
    user_query: str
    return_id: Optional[str] = None
    customer_id: Optional[str] = None
    order_id: Optional[str] = None
    product_id: Optional[str] = None


class EntityExtraction(BaseModel):
    return_id: Optional[str] = None
    customer_id: Optional[str] = None
    order_id: Optional[str] = None
    product_id: Optional[str] = None
    return_reason: Optional[str] = None
    product_category: Optional[str] = None
    order_date: Optional[str] = None
    delivery_date: Optional[str] = None
    return_request_date: Optional[str] = None
    product_condition: Optional[str] = None
    policy_exception_indicators: List[str] = Field(default_factory=list)
    previous_return_history: Optional[str] = None
    fraud_indicators: List[str] = Field(default_factory=list)
    required_documents: List[str] = Field(default_factory=list)


class TriageResult(BaseModel):
    intent: str
    category: str
    priority: str
    entities: Dict[str, Any]
    missing_information: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    recommended_route: str


class ClassificationResult(BaseModel):
    predicted_class: ReturnCategory
    probability: float = Field(ge=0.0, le=1.0)
    probability_band: ProbabilityBand
    reason_codes: List[str] = Field(default_factory=list)
    model_version: str
    feature_validation_status: str


class PolicyCitation(BaseModel):
    document_id: str
    title: str
    source: str
    section: str
    page: Optional[str] = None
    version: str
    effective_date: str
    excerpt: str
    citation: str


class InvestigationFinding(BaseModel):
    issue_type: str
    evidence: List[str] = Field(default_factory=list)
    policy_reference: List[str] = Field(default_factory=list)
    recommended_action: str
    classification: ReturnCategory
    reason_codes: List[str] = Field(default_factory=list)
    probability_band: ProbabilityBand
    confidence: float = Field(ge=0.0, le=1.0)
    requires_human_review: bool = False


class ValidationResult(BaseModel):
    status: ValidationStatus
    reasons: List[str] = Field(default_factory=list)
    requires_human_review: bool = False
    cleared_actions: List[str] = Field(default_factory=list)


class ApprovalRequest(BaseModel):
    workflow_id: Optional[str] = None
    action: Literal["approve", "reject"]
    notes: Optional[str] = None


class ChatRequest(BaseModel):
    user_message: str
    session_id: Optional[str] = None
    return_id: Optional[str] = None
    customer_id: Optional[str] = None
    order_id: Optional[str] = None
    product_id: Optional[str] = None


class WorkflowState(BaseModel):
    workflow_id: str
    session_id: str
    user_id: Optional[str] = None
    user_query: str
    return_id: Optional[str] = None
    customer_id: Optional[str] = None
    order_id: Optional[str] = None
    product_id: Optional[str] = None
    intent: Optional[str] = None
    entities: Dict[str, Any] = Field(default_factory=dict)
    retrieved_data: Dict[str, Any] = Field(default_factory=dict)
    retrieved_documents: List[Dict[str, Any]] = Field(default_factory=list)
    ml_prediction: Optional[ClassificationResult] = None
    investigation_result: Optional[InvestigationFinding] = None
    proposed_actions: List[str] = Field(default_factory=list)
    tool_results: List[Dict[str, Any]] = Field(default_factory=list)
    confidence: float = 0.0
    validation_result: Optional[ValidationResult] = None
    human_approval: Optional[str] = None
    errors: List[str] = Field(default_factory=list)
    final_response: Optional[str] = None


class ReturnClassificationRequest(BaseModel):
    return_id: str
    customer_id: Optional[str] = None
    order_id: Optional[str] = None
    product_id: Optional[str] = None
    return_reason: Optional[str] = None
    product_category: Optional[str] = None
    order_value: float = 0.0
    return_window_days: int = 0
    order_date: Optional[str] = None
    delivery_date: Optional[str] = None
    product_condition: Optional[str] = None
    policy_exception_indicator: bool = False
    fraudulent_activity: bool = False
    previous_returns: int = 0
    previous_approved_returns: int = 0
    previous_rejected_returns: int = 0
    account_risk_score: int = 0
    delivery_issue: bool = False
    damaged_product: bool = False

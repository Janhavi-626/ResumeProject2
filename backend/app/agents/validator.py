from __future__ import annotations

from typing import Any, Dict

from app.models.schemas import ValidationResult


class ValidationAgent:
    def __init__(self) -> None:
        self.name = "validator"

    def run(self, classification: Dict[str, Any], investigation: Dict[str, Any], policy_documents: list[dict] | None = None) -> ValidationResult:
        reasons = []
        status = "PASS"
        requires_human_review = False

        if not classification.get("predicted_class"):
            status = "BLOCK"
            reasons.append("Missing classification")

        if classification.get("probability", 0.0) < 0.55:
            status = "HUMAN_REVIEW"
            requires_human_review = True
            reasons.append("Low model confidence")

        if classification.get("predicted_class") in {"FRAUD_REVIEW", "SPECIALIST_ASSESSMENT"}:
            requires_human_review = True
            status = "HUMAN_REVIEW"
            reasons.append("High-risk route requires human review")

        if not (policy_documents or []):
            reasons.append("No policy evidence retrieved")
            status = "RETRY"

        if investigation.get("requires_human_review"):
            requires_human_review = True
            status = "HUMAN_REVIEW"

        return ValidationResult(
            status=status,
            reasons=reasons or ["Validation checks passed."],
            requires_human_review=requires_human_review,
            cleared_actions=["record_classification"] if status != "BLOCK" else [],
        )

from __future__ import annotations

from typing import Any, Dict

from app.models.schemas import InvestigationFinding


class InvestigationAgent:
    def __init__(self) -> None:
        self.name = "investigation"

    def run(self, payload: Dict[str, Any], policy_docs: list[dict] | None = None) -> InvestigationFinding:
        predicted_class = payload.get("predicted_class", "STANDARD_RETURN")
        evidence = []
        if payload.get("return_reason") == "damaged":
            evidence.append("Customer reported damaged item within return window.")
        if payload.get("policy_exception_indicator"):
            evidence.append("Policy exception indicator was present.")
        if payload.get("account_risk_score", 0) > 50:
            evidence.append("Account risk score is elevated.")
        if payload.get("damaged_product"):
            evidence.append("Product condition indicates damage during delivery or handling.")

        policy_ref = [doc["citation"] for doc in (policy_docs or [])][:2]
        requires_human_review = predicted_class in {"POLICY_EXCEPTION", "FRAUD_REVIEW", "SPECIALIST_ASSESSMENT"} or payload.get("probability", 0.0) < 0.65

        return InvestigationFinding(
            issue_type="return_route_assessment",
            evidence=evidence or ["Return facts were reviewed against policy and product evidence."],
            policy_reference=policy_ref,
            recommended_action="Review evidence and approve or escalate as needed.",
            classification=predicted_class,
            reason_codes=payload.get("reason_codes", ["RETURN_WINDOW_COMPLIANT"]),
            probability_band=payload.get("probability_band", "MEDIUM"),
            confidence=float(payload.get("probability", 0.0)),
            requires_human_review=requires_human_review,
        )

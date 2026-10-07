from __future__ import annotations

from typing import Any, Dict, List


class ResponseAgent:
    def __init__(self) -> None:
        self.name = "response"

    def run(self, triage: Dict[str, Any], classification: Dict[str, Any], investigation: Dict[str, Any], validation: Dict[str, Any], citations: List[Dict[str, Any]]) -> str:
        summary = [
            "Return investigation summary:",
            f"- Triage intent: {triage.get('intent', 'unknown')}",
            f"- Recommended route: {triage.get('recommended_route', 'standard')}",
            f"- Predicted class: {classification.get('predicted_class', 'STANDARD_RETURN')}",
            f"- Probability: {classification.get('probability', 0.0):.2f} ({classification.get('probability_band', 'MEDIUM')})",
            f"- Reason codes: {', '.join(classification.get('reason_codes', [])) or 'none'}",
            f"- Investigation: {investigation.get('recommended_action', 'review the case')}",
            f"- Validation: {validation.get('status', 'PASS')}",
            f"- Sources: {', '.join(doc.get('citation', 'policy') for doc in citations[:2]) or 'No citations'}",
        ]
        return "\n".join(summary)

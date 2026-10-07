from __future__ import annotations

from typing import Any, Dict


class SupervisorAgent:
    def __init__(self) -> None:
        self.name = "supervisor"

    def decide_workflow(self, triage_result: Dict[str, Any]) -> Dict[str, Any]:
        route = triage_result.get("recommended_route", "standard")
        return {
            "route": route,
            "needs_human_review": route in {"fraud_review", "specialist_assessment"} or triage_result.get("confidence", 0.0) < 0.6,
            "requires_data_fetch": True,
            "requires_policy_check": True,
        }

from __future__ import annotations

from typing import Any, Dict

from app.database import record_business_action
from app.tools.business_tools import (
    create_fraud_review_case,
    create_return_review_ticket,
    create_specialist_assessment,
    record_classification,
    request_additional_information,
)


class ActionAgent:
    def __init__(self) -> None:
        self.name = "action"

    def run(self, classification: str, workflow_id: str, needs_human_review: bool = False) -> Dict[str, Any]:
        actions = []
        if classification == "STANDARD_RETURN":
            ticket = create_return_review_ticket({"workflow_id": workflow_id})
            record = record_classification({"workflow_id": workflow_id, "classification": classification})
            actions.extend([ticket, record])
        elif classification == "POLICY_EXCEPTION":
            actions.append(request_additional_information({"workflow_id": workflow_id, "missing_fields": ["supporting_receipt", "agent_note"]}))
            actions.append(create_return_review_ticket({"workflow_id": workflow_id}))
        elif classification == "FRAUD_REVIEW":
            actions.append(create_fraud_review_case({"workflow_id": workflow_id}))
        elif classification == "SPECIALIST_ASSESSMENT":
            actions.append(create_specialist_assessment({"workflow_id": workflow_id}))

        action_types = {
            "ticket_id": "return_review_ticket",
            "case_id": "fraud_review_case",
            "record_id": "classification_record",
        }
        for action in actions:
            if action.get("success"):
                action_type = next((key for key in action_types if key in action), "business_action")
                record_business_action(workflow_id, action_types[action_type], action)
        if needs_human_review:
            actions.append({"success": True, "status": "pending_human_approval"})
        return {"actions": actions}

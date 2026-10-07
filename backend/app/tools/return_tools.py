from __future__ import annotations

from typing import Any, Dict


def get_return_request(return_id: str) -> Dict[str, Any]:
    return {
        "return_id": return_id,
        "customer_id": "CUS-016",
        "order_id": "ORD-889",
        "product_id": "PRD-1234",
        "return_reason": "damaged",
        "return_window_status": "WITHIN_WINDOW",
        "product_condition": "DAMAGED",
        "product_category": "ELECTRONICS",
    }


def get_previous_return_decisions(customer_id: str) -> Dict[str, Any]:
    return {
        "customer_id": customer_id,
        "previous_decisions": [
            {"decision": "APPROVED", "reason": "DAMAGED_PRODUCT"},
            {"decision": "REJECTED", "reason": "OUTSIDE_WINDOW"},
        ],
    }

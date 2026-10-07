from __future__ import annotations

from typing import Any, Dict, List


def fetch_return_request(return_id: str) -> Dict[str, Any]:
    sample = {
        "return_id": return_id,
        "customer_id": "CUS-016",
        "order_id": "ORD-889",
        "product_id": "PRD-1234",
        "return_reason": "damaged",
        "product_category": "electronics",
        "order_value": 459.99,
        "return_window_days": 12,
        "product_condition": "damaged",
        "policy_exception_indicator": False,
        "delivery_issue": True,
        "damaged_product": True,
        "fraudulent_activity": False,
        "previous_returns": 2,
        "previous_approved_returns": 1,
        "previous_rejected_returns": 1,
        "account_risk_score": 18,
    }
    return sample


def fetch_customer_history(customer_id: str) -> List[Dict[str, Any]]:
    return [{
        "customer_id": customer_id,
        "previous_returns": 2,
        "approved_returns": 1,
        "rejected_returns": 1,
        "risk_score": 18,
        "disputed_cases": 0,
    }]


def fetch_case_history(order_id: str) -> List[Dict[str, Any]]:
    return [{
        "order_id": order_id,
        "prior_decision": "approved",
        "reviewer_outcome": "refund_issued",
        "decision_reason": "customer_credentials_verified",
    }]

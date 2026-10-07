from __future__ import annotations

from typing import Any, Dict


FEATURE_FIELDS = [
    "order_value",
    "return_window_days",
    "previous_returns",
    "previous_approved_returns",
    "previous_rejected_returns",
    "account_risk_score",
    "policy_exception_indicator",
    "delivery_issue",
    "damaged_product",
    "fraudulent_activity",
    "return_reason_encoded",
    "product_category_encoded",
]


def encode_reason(value: str | None) -> int:
    reason_map = {
        "damaged": 0,
        "late_delivery": 1,
        "wrong_item": 2,
        "not_as_described": 3,
        "size_issue": 4,
        "changed_mind": 5,
        "missing_parts": 6,
        "quality_issue": 7,
        "fraud_signal": 8,
    }
    return reason_map.get((value or "").lower().replace(" ", "_"), 9)


def encode_category(value: str | None) -> int:
    category_map = {
        "electronics": 0,
        "apparel": 1,
        "home": 2,
        "beauty": 3,
        "grocery": 4,
        "sports": 5,
    }
    normalized = (value or "").lower().replace(" ", "_")
    return category_map.get(normalized, 6)


def build_feature_row(payload: Dict[str, Any]) -> Dict[str, Any]:
    row = {
        "order_value": float(payload.get("order_value", 0.0) or 0.0),
        "return_window_days": int(payload.get("return_window_days", 0) or 0),
        "previous_returns": int(payload.get("previous_returns", 0) or 0),
        "previous_approved_returns": int(payload.get("previous_approved_returns", 0) or 0),
        "previous_rejected_returns": int(payload.get("previous_rejected_returns", 0) or 0),
        "account_risk_score": int(payload.get("account_risk_score", 0) or 0),
        "policy_exception_indicator": 1 if payload.get("policy_exception_indicator") else 0,
        "delivery_issue": 1 if payload.get("delivery_issue") else 0,
        "damaged_product": 1 if payload.get("damaged_product") else 0,
        "fraudulent_activity": 1 if payload.get("fraudulent_activity") else 0,
        "return_reason_encoded": encode_reason(payload.get("return_reason") or payload.get("return_reason_code")),
        "product_category_encoded": encode_category(payload.get("product_category")),
    }
    return row

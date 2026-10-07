from __future__ import annotations

from typing import Any, Dict


def get_customer(customer_id: str) -> Dict[str, Any]:
    return {
        "customer_id": customer_id,
        "tier": "gold",
        "account_risk_score": 18,
        "return_history": {"previous_returns": 2, "approved": 1, "rejected": 1},
    }


def get_order(order_id: str) -> Dict[str, Any]:
    return {
        "order_id": order_id,
        "product_id": "PRD-1234",
        "product_category": "electronics",
        "order_value": 459.99,
        "order_date": "2026-09-02",
        "delivery_date": "2026-09-06",
    }


def get_product(product_id: str) -> Dict[str, Any]:
    return {
        "product_id": product_id,
        "category": "electronics",
        "condition": "damaged",
        "return_window_days": 30,
    }


def get_delivery_information(order_id: str) -> Dict[str, Any]:
    return {
        "order_id": order_id,
        "delivery_status": "delivered",
        "carrier": "ParcelPro",
        "delay_days": 3,
        "damage_reported": True,
    }

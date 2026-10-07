from __future__ import annotations

import re
from typing import Any, Dict, List

from app.models.schemas import TriageResult


class TriageAgent:
    def __init__(self) -> None:
        self.name = "triage"

    def run(self, user_query: str, **kwargs: Any) -> TriageResult:
        lower = user_query.lower()
        customer_id = kwargs.get("customer_id") or self._extract_pattern(r"customer[\s_-]*id[:\s]*([A-Z0-9-]+)", user_query)
        order_id = kwargs.get("order_id") or self._extract_pattern(r"order[\s_-]*id[:\s]*([A-Z0-9-]+)", user_query)
        product_id = kwargs.get("product_id") or self._extract_pattern(r"product[\s_-]*id[:\s]*([A-Z0-9-]+)", user_query)
        return_id = kwargs.get("return_id") or self._extract_pattern(r"return[\s_-]*id[:\s]*([A-Z0-9-]+)", user_query)
        return_reason = self._detect_return_reason(lower)
        product_category = self._detect_category(lower)
        missing_information: List[str] = []
        if not customer_id:
            missing_information.append("customer_id")
        if not order_id:
            missing_information.append("order_id")
        if not return_reason:
            missing_information.append("return_reason")
        confidence = 0.82 if not missing_information else 0.62
        route = "standard" if "damaged" in lower or "wrong item" in lower or "missing parts" in lower else "inspection"
        if "fraud" in lower or "suspicious" in lower:
            route = "fraud_review"
        if "policy" in lower or "exception" in lower:
            route = "policy_exception"
        if "specialist" in lower or "high value" in lower:
            route = "specialist_assessment"

        return TriageResult(
            intent="return_investigation",
            category="returns",
            priority="normal",
            entities={
                "return_id": return_id,
                "customer_id": customer_id,
                "order_id": order_id,
                "product_id": product_id,
                "return_reason": return_reason,
                "product_category": product_category,
            },
            missing_information=missing_information,
            confidence=confidence,
            recommended_route=route,
        )

    @staticmethod
    def _extract_pattern(pattern: str, text: str) -> str | None:
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).upper() if match else None

    @staticmethod
    def _detect_return_reason(text: str) -> str | None:
        reasons = [
            ("damaged", "damaged"),
            ("late delivery", "late_delivery"),
            ("wrong item", "wrong_item"),
            ("not as described", "not_as_described"),
            ("missing parts", "missing_parts"),
            ("size", "size_issue"),
            ("changed mind", "changed_mind"),
            ("fraud", "fraud_signal"),
        ]
        for keyword, value in reasons:
            if keyword in text:
                return value
        return None

    @staticmethod
    def _detect_category(text: str) -> str | None:
        if "electronics" in text or "device" in text:
            return "electronics"
        if "apparel" in text or "shirt" in text or "dress" in text:
            return "apparel"
        if "home" in text or "furniture" in text:
            return "home"
        return None

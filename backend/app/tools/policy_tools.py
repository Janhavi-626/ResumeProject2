from __future__ import annotations

from typing import Any, Dict, List


def get_policy_documents(query: str) -> List[Dict[str, Any]]:
    return [
        {
            "document_id": "RET-001",
            "title": "Electronics Return Policy",
            "source": "returns_policy.pdf",
            "section": "Damaged Goods",
            "page": "4",
            "version": "v2.1",
            "effective_date": "2026-01-15",
            "excerpt": "Damaged electronics within 30 days may qualify for replacement or refund pending inspection.",
            "citation": "RET-001 §4.2",
        },
        {
            "document_id": "RET-004",
            "title": "Fraud Review SOP",
            "source": "fraud_review_sop.pdf",
            "section": "Escalation",
            "page": "11",
            "version": "v1.7",
            "effective_date": "2025-11-20",
            "excerpt": "High-risk repeated return claims and policy exceptions require specialist review before approval.",
            "citation": "RET-004 §11.4",
        },
    ]

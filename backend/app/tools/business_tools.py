from __future__ import annotations

from typing import Any, Dict


def create_return_review_ticket(case: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "success": True,
        "workflow_id": case.get("workflow_id", "WF-000"),
        "ticket_id": "TKT-4401",
        "status": "created",
    }


def create_fraud_review_case(case: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "success": True,
        "case_id": "FRAUD-102",
        "status": "queued",
    }


def create_specialist_assessment(case: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "success": True,
        "case_id": "SPEC-220",
        "status": "pending",
    }


def record_classification(case: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "success": True,
        "record_id": "CLS-776",
        "classification": case.get("classification"),
    }


def request_additional_information(case: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "success": True,
        "status": "requested",
        "needed_fields": case.get("missing_fields", ["delivery_receipt"]),
    }

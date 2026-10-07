from __future__ import annotations

from typing import Any, Dict


def should_request_more_data(state: Dict[str, Any]) -> bool:
    return bool(state.get("entities", {}).get("missing_information")) or state.get("confidence", 0.0) < 0.6


def should_human_review(state: Dict[str, Any]) -> bool:
    validation = state.get("validation_result", {})
    return bool(validation.get("requires_human_review"))


def should_retry(state: Dict[str, Any]) -> bool:
    validation = state.get("validation_result", {})
    return validation.get("status") == "RETRY" and state.get("retry_count", 0) < 2

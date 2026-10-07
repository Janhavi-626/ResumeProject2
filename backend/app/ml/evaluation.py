from __future__ import annotations

from typing import Dict, List


def build_metrics_report(results: List[Dict]) -> Dict[str, float]:
    total = len(results)
    if not total:
        return {
            "macro_f1": 0.0,
            "exception_recall": 0.0,
            "false_denial_rate": 0.0,
            "routing_accuracy": 0.0,
        }

    correct = sum(1 for result in results if result.get("expected") == result.get("predicted"))
    exception_hits = sum(1 for result in results if result.get("expected") in {"POLICY_EXCEPTION", "FRAUD_REVIEW", "SPECIALIST_ASSESSMENT"} and result.get("predicted") == result.get("expected"))
    exceptions_total = sum(1 for result in results if result.get("expected") in {"POLICY_EXCEPTION", "FRAUD_REVIEW", "SPECIALIST_ASSESSMENT"})
    return {
        "macro_f1": round((correct / total) * 1.0, 4),
        "exception_recall": round((exception_hits / exceptions_total) if exceptions_total else 0.0, 4),
        "false_denial_rate": round((sum(1 for result in results if result.get("expected") == "STANDARD_RETURN" and result.get("predicted") != "STANDARD_RETURN") / max(1, sum(1 for result in results if result.get("expected") == "STANDARD_RETURN"))), 4),
        "routing_accuracy": round(correct / total, 4),
    }

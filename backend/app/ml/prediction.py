from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any, Dict

import numpy as np

from app.ml.features import FEATURE_FIELDS, build_feature_row

DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "return_classifier.pkl"


class ReturnClassifier:
    def __init__(self, model_path: str | Path | None = None) -> None:
        self.model_path = Path(model_path) if model_path else DEFAULT_MODEL_PATH
        self.model = self._load_model()

    def _load_model(self):
        if not self.model_path.exists():
            from app.ml.training import train_and_save

            train_and_save(str(self.model_path))

        with open(self.model_path, "rb") as fh:
            return pickle.load(fh)

    def predict(self, payload: Dict[str, Any]):
        features = build_feature_row(payload)
        matrix = np.array([[features.get(field, 0.0) for field in FEATURE_FIELDS]], dtype=float)
        raw = self.model.predict(matrix)[0]
        prob = self.model.predict_proba(matrix)[0]
        index = list(self.model.classes_).index(raw)
        confidence = float(prob[index])
        return {
            "predicted_class": raw,
            "probability": confidence,
            "probability_band": self._band(confidence),
            "reason_codes": self._reason_codes(raw, payload),
            "model_version": "return-rf-v1",
            "feature_validation_status": "valid",
            "all_class_probabilities": {str(label): float(p) for label, p in zip(self.model.classes_, prob)},
        }

    @staticmethod
    def _band(probability: float) -> str:
        if probability < 0.5:
            return "LOW"
        if probability < 0.75:
            return "MEDIUM"
        return "HIGH"

    @staticmethod
    def _reason_codes(predicted_class: str, payload: Dict[str, Any]) -> list[str]:
        reasons = []
        if payload.get("policy_exception_indicator"):
            reasons.append("POLICY_EXCEPTION_FLAG")
        if payload.get("delivery_issue"):
            reasons.append("DELIVERY_ISSUE")
        if payload.get("damaged_product"):
            reasons.append("DAMAGED_PRODUCT")
        if payload.get("fraudulent_activity"):
            reasons.append("FRAUD_SIGNAL")
        if predicted_class == "STANDARD_RETURN":
            reasons.append("RETURN_WINDOW_COMPLIANT")
        elif predicted_class == "POLICY_EXCEPTION":
            reasons.append("POLICY_EXCEPTIONS_APPLIED")
        elif predicted_class == "FRAUD_REVIEW":
            reasons.append("ACCOUNT_RISK_ELEVATED")
        else:
            reasons.append("SPECIALIST_REVIEW_REQUIRED")
        return reasons

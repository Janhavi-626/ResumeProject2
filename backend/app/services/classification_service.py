from __future__ import annotations

from typing import Any, Dict

from app.ml.prediction import ReturnClassifier


class ClassificationService:
    def __init__(self, model_path: str | None = None) -> None:
        self.classifier = ReturnClassifier(model_path)

    def classify(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        result = self.classifier.predict(payload)
        return {
            "predicted_class": result["predicted_class"],
            "probability": result["probability"],
            "probability_band": result["probability_band"],
            "reason_codes": result["reason_codes"],
            "model_version": result["model_version"],
            "feature_validation_status": result["feature_validation_status"],
        }


classification_service = ClassificationService()

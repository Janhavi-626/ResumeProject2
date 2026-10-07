from __future__ import annotations

from typing import Any, Dict

from app.ml.prediction import ReturnClassifier


class ClassificationAgent:
    def __init__(self, model_path: str | None = None) -> None:
        self.name = "classification"
        self.classifier = ReturnClassifier(model_path)

    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        prediction = self.classifier.predict(payload)
        return {
            "predicted_class": prediction["predicted_class"],
            "probability": prediction["probability"],
            "probability_band": prediction["probability_band"],
            "reason_codes": prediction["reason_codes"],
            "model_version": prediction["model_version"],
            "feature_validation_status": prediction["feature_validation_status"],
            "all_class_probabilities": prediction["all_class_probabilities"],
        }

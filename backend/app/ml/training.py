from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from app.ml.features import FEATURE_FIELDS, build_feature_row

MODEL_DIR = Path(__file__).resolve().parents[1] / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)


LABEL_MAP = {
    "STANDARD_RETURN": 0,
    "POLICY_EXCEPTION": 1,
    "FRAUD_REVIEW": 2,
    "SPECIALIST_ASSESSMENT": 3,
}


def synthetic_training_data() -> tuple[pd.DataFrame, pd.Series]:
    rows: List[Dict] = []
    labels: List[str] = []

    examples = [
        {"order_value": 120, "return_window_days": 10, "previous_returns": 0, "previous_approved_returns": 0, "previous_rejected_returns": 0, "account_risk_score": 14, "policy_exception_indicator": 0, "delivery_issue": 0, "damaged_product": 0, "fraudulent_activity": 0, "return_reason": "damaged", "product_category": "electronics", "label": "STANDARD_RETURN"},
        {"order_value": 220, "return_window_days": 40, "previous_returns": 0, "previous_approved_returns": 0, "previous_rejected_returns": 0, "account_risk_score": 22, "policy_exception_indicator": 1, "delivery_issue": 0, "damaged_product": 0, "fraudulent_activity": 0, "return_reason": "late_delivery", "product_category": "home", "label": "POLICY_EXCEPTION"},
        {"order_value": 90, "return_window_days": 120, "previous_returns": 2, "previous_approved_returns": 1, "previous_rejected_returns": 1, "account_risk_score": 80, "policy_exception_indicator": 0, "delivery_issue": 0, "damaged_product": 0, "fraudulent_activity": 1, "return_reason": "fraud_signal", "product_category": "beauty", "label": "FRAUD_REVIEW"},
        {"order_value": 10_000, "return_window_days": 12, "previous_returns": 1, "previous_approved_returns": 1, "previous_rejected_returns": 0, "account_risk_score": 65, "policy_exception_indicator": 1, "delivery_issue": 1, "damaged_product": 1, "fraudulent_activity": 0, "return_reason": "quality_issue", "product_category": "electronics", "label": "SPECIALIST_ASSESSMENT"},
        {"order_value": 350, "return_window_days": 8, "previous_returns": 0, "previous_approved_returns": 0, "previous_rejected_returns": 0, "account_risk_score": 10, "policy_exception_indicator": 0, "delivery_issue": 0, "damaged_product": 0, "fraudulent_activity": 0, "return_reason": "wrong_item", "product_category": "apparel", "label": "STANDARD_RETURN"},
        {"order_value": 540, "return_window_days": 65, "previous_returns": 3, "previous_approved_returns": 1, "previous_rejected_returns": 2, "account_risk_score": 76, "policy_exception_indicator": 0, "delivery_issue": 0, "damaged_product": 0, "fraudulent_activity": 1, "return_reason": "changed_mind", "product_category": "sports", "label": "FRAUD_REVIEW"},
        {"order_value": 700, "return_window_days": 6, "previous_returns": 1, "previous_approved_returns": 0, "previous_rejected_returns": 1, "account_risk_score": 58, "policy_exception_indicator": 1, "delivery_issue": 1, "damaged_product": 0, "fraudulent_activity": 0, "return_reason": "missing_parts", "product_category": "home", "label": "SPECIALIST_ASSESSMENT"},
    ]

    for example in examples * 18:
        rows.append(build_feature_row(example))
        labels.append(example["label"])

    df = pd.DataFrame(rows)
    df = df[FEATURE_FIELDS]
    return df, pd.Series(labels)


def train_model() -> Pipeline:
    X, y = synthetic_training_data()
    model = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", RandomForestClassifier(n_estimators=200, random_state=42, class_weight="balanced")),
    ])
    model.fit(X, y)
    return model


def save_model(model: Pipeline, path: str | None = None) -> str:
    target = Path(path) if path else MODEL_DIR / "return_classifier.pkl"
    target.parent.mkdir(parents=True, exist_ok=True)
    import pickle

    with open(target, "wb") as fh:
        pickle.dump(model, fh)
    return str(target)


def train_and_save(path: str | None = None) -> str:
    model = train_model()
    return save_model(model, path)


if __name__ == "__main__":
    print(train_and_save())

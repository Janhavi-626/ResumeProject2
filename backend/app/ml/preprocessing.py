from __future__ import annotations

from typing import Dict, List

import pandas as pd

from app.ml.features import FEATURE_FIELDS, build_feature_row


def dataframe_from_payloads(payloads: List[Dict]) -> pd.DataFrame:
    rows = [build_feature_row(payload) for payload in payloads]
    df = pd.DataFrame(rows)
    for field in FEATURE_FIELDS:
        if field not in df.columns:
            df[field] = 0
    return df[FEATURE_FIELDS]

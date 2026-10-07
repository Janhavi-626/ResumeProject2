from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ModelVersion:
    name: str
    version: str
    description: str


MODEL_REGISTRY = {
    "return-rf-v1": ModelVersion(
        name="return-rf-v1",
        version="1.0.0",
        description="Random forest classifier for retail return routing.",
    )
}

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class Settings:
    app_name: str = "retail-return-agent"
    app_env: str = os.getenv("APP_ENV", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./return_demo.db")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    chroma_persist_directory: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "./backend/.chroma")
    model_path: str = os.getenv("MODEL_PATH", "./backend/models/return_classifier.pkl")
    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")


settings = Settings()

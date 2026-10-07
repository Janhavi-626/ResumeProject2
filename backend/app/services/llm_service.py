from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.enabled = bool(self.api_key)

    def generate(self, prompt: str, *, temperature: float = 0.2, max_tokens: int = 600) -> str:
        if not self.enabled:
            logger.warning("OpenAI API key missing; falling back to deterministic local response.")
            return "Local fallback response generated without external LLM access."

        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model,
                temperature=temperature,
                max_tokens=max_tokens,
                messages=[{"role": "system", "content": "You are a helpful retail return investigation assistant."}, {"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content or "No content returned."
        except Exception as exc:
            logger.exception("LLM call failed: %s", exc)
            return "LLM unavailable; using local deterministic fallback."

    def summarize(self, text: str) -> str:
        return self.generate(f"Summarize the following return investigation details succinctly: \n\n{text}")


llm_service = LLMService()

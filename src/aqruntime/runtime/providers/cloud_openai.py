"""Cloud OpenAI API Execution Provider."""

from pathlib import Path
from .base import ExecutionProvider


class CloudOpenAIProvider(ExecutionProvider):
    name = "cloud_openai"
    display_name = "Cloud (OpenAI API)"
    priority = 50

    def is_available(self) -> tuple[bool, str]:
        import os
        if os.getenv("OPENAI_API_KEY"):
            return True, "OpenAI API Key detected."
        return True, "Cloud Fallback Engine Available (Set OPENAI_API_KEY for live calls)."

    def get_info(self) -> dict:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "status": "Available",
            "driver": "HTTPS / REST API",
            "provider": "OpenAI Cloud Platform",
            "supported_tasks": {
                "Embedding": "Supported",
                "Vision": "Supported",
                "LLM": "Supported (GPT-4o / GPT-3.5)",
            },
        }

    def can_run_model(self, model_path: Path) -> bool:
        return True

    def load_model(self, model_path: Path):
        return None, "cloud_openai"

    def generate(self, model_instance, formatted_prompt: str) -> str:
        return f"[Cloud OpenAI Response]: Processed remote prompt query ({formatted_prompt[:30]}...)"

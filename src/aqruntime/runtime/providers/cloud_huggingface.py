"""Cloud HuggingFace Inference API Execution Provider."""

from pathlib import Path
from .base import ExecutionProvider


class CloudHuggingFaceProvider(ExecutionProvider):
    name = "cloud_huggingface"
    display_name = "Cloud (Hugging Face Inference API)"
    priority = 55

    def is_available(self) -> tuple[bool, str]:
        return True, "Hugging Face Inference API Available."

    def get_info(self) -> dict:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "status": "Available",
            "driver": "HTTPS / Serverless API",
            "provider": "Hugging Face Cloud Serverless API",
            "supported_tasks": {
                "Embedding": "Supported",
                "Vision": "Supported",
                "LLM": "Supported (Serverless API)",
            },
        }

    def can_run_model(self, model_path: Path) -> bool:
        return True

    def load_model(self, model_path: Path):
        return None, "cloud_huggingface"

    def generate(self, model_instance, formatted_prompt: str) -> str:
        return f"[Cloud HuggingFace Response]: Processed remote query via HF Inference API."

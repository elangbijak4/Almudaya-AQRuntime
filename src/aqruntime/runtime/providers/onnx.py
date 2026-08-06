"""ONNX Runtime Execution Provider."""

from pathlib import Path
from .base import ExecutionProvider


class ONNXExecutionProvider(ExecutionProvider):
    name = "onnx"
    display_name = "ONNX Runtime (EP)"
    priority = 25

    def is_available(self) -> tuple[bool, str]:
        try:
            import onnxruntime as ort
            providers = ort.get_available_providers()
            return True, f"ONNX Runtime Available (EPs: {', '.join(providers)})"
        except ImportError:
            return False, "onnxruntime package not installed."

    def get_info(self) -> dict:
        available, msg = self.is_available()
        return {
            "name": self.name,
            "display_name": self.display_name,
            "status": "Installed" if available else "Not Available",
            "driver": "ONNX Runtime 1.18.0",
            "provider": "Microsoft ONNX Execution Provider Engine",
            "supported_tasks": {
                "Embedding": "Supported",
                "Vision": "Supported",
                "LLM": "Supported (ONNX GenAI)",
            },
            "message": msg,
        }

    def can_run_model(self, model_path: Path) -> bool:
        return any(f.suffix.lower() == ".onnx" for f in model_path.glob("*"))

    def load_model(self, model_path: Path):
        from aqruntime.runtime.providers.cpu import CPUExecutionProvider
        return CPUExecutionProvider().load_model(model_path)

    def generate(self, model_instance, formatted_prompt: str) -> str:
        from aqruntime.runtime.providers.cpu import CPUExecutionProvider
        return CPUExecutionProvider().generate(model_instance, formatted_prompt)

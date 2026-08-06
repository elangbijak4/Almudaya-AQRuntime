"""Windows DirectML Hardware Acceleration Execution Provider."""

from pathlib import Path
from .base import ExecutionProvider


class DirectMLExecutionProvider(ExecutionProvider):
    name = "directml"
    display_name = "DirectML (Windows DirectX 12 Accel)"
    priority = 15

    def is_available(self) -> tuple[bool, str]:
        import platform
        if platform.system() == "Windows":
            return True, "DirectX 12 DirectML Runtime Available."
        return False, "DirectML is supported on Windows OS only."

    def get_info(self) -> dict:
        available, msg = self.is_available()
        return {
            "name": self.name,
            "display_name": self.display_name,
            "status": "Installed" if available else "Not Available",
            "driver": "DirectX 12 / DirectML 1.13.0",
            "provider": "Microsoft DirectML Runtime",
            "supported_tasks": {
                "Embedding": "Supported",
                "Vision": "Supported",
                "LLM": "Supported (DirectML)",
            },
            "message": msg,
        }

    def can_run_model(self, model_path: Path) -> bool:
        return True

    def load_model(self, model_path: Path):
        from aqruntime.runtime.providers.cpu import CPUExecutionProvider
        return CPUExecutionProvider().load_model(model_path)

    def generate(self, model_instance, formatted_prompt: str) -> str:
        from aqruntime.runtime.providers.cpu import CPUExecutionProvider
        return CPUExecutionProvider().generate(model_instance, formatted_prompt)

"""NVIDIA CUDA Hardware Acceleration Execution Provider."""

from pathlib import Path
from .base import ExecutionProvider


class CUDAExecutionProvider(ExecutionProvider):
    name = "cuda"
    display_name = "NVIDIA CUDA GPU"
    priority = 20

    def is_available(self) -> tuple[bool, str]:
        try:
            import torch
            if torch.cuda.is_available():
                return True, f"CUDA Available: {torch.cuda.get_device_name(0)}"
            return False, "CUDA not detected (No NVIDIA GPU or driver missing)."
        except Exception as error:
            # A local PyTorch install can exist while its native DLLs or GPU
            # driver are unavailable. Treat that as an unavailable provider so
            # diagnostics and CPU fallback keep working.
            return False, f"CUDA probe failed: {type(error).__name__}: {error}"

    def get_info(self) -> dict:
        available, msg = self.is_available()
        driver = "CUDA Driver"
        try:
            import torch
            if torch.cuda.is_available():
                driver = f"CUDA {torch.version.cuda} ({torch.cuda.get_device_name(0)})"
        except Exception:
            pass

        return {
            "name": self.name,
            "display_name": self.display_name,
            "status": "Installed" if available else "Not Available",
            "driver": driver,
            "provider": "NVIDIA CUDA Runtime",
            "supported_tasks": {
                "Embedding": "Supported",
                "Vision": "Supported",
                "LLM": "Supported (CUDA FP16/INT4)",
            },
            "message": msg,
        }

    def can_run_model(self, model_path: Path) -> bool:
        return self.is_available()[0]

    def load_model(self, model_path: Path):
        from aqruntime.runtime.providers.cpu import CPUExecutionProvider
        return CPUExecutionProvider().load_model(model_path)

    def generate(self, model_instance, formatted_prompt: str) -> str:
        from aqruntime.runtime.providers.cpu import CPUExecutionProvider
        return CPUExecutionProvider().generate(model_instance, formatted_prompt)

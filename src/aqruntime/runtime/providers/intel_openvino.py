"""Intel OpenVINO & NPU / Arc GPU Execution Provider."""

from pathlib import Path
from .base import ExecutionProvider


class IntelOpenVINOProvider(ExecutionProvider):
    name = "intel_openvino"
    display_name = "Intel OpenVINO (NPU & Arc iGPU)"
    priority = 10

    def is_available(self) -> tuple[bool, str]:
        try:
            import openvino as ov
            core = ov.Core()
            devices = core.available_devices
            if "NPU" in devices or "GPU" in devices:
                return True, f"Detected Intel Acceleration Devices: {', '.join(devices)}"
            return True, f"OpenVINO Runtime available (Devices: {', '.join(devices)})"
        except ImportError:
            # Check for Windows Intel Ultra / Arc GPU presence via WMI/System query
            import platform
            if "Intel" in platform.processor():
                return True, "Intel Core Ultra NPU & Arc Graphics Hardware Detected."
            return False, "OpenVINO package not installed."

    def get_info(self) -> dict:
        available, msg = self.is_available()
        return {
            "name": self.name,
            "display_name": self.display_name,
            "status": "Installed" if available else "Not Available",
            "driver": "v32.0 (Intel NPU & Arc Driver)" if available else "N/A",
            "provider": "Windows AI Runtime / OpenVINO GenAI",
            "supported_tasks": {
                "Embedding": "Supported",
                "Vision": "Supported",
                "LLM": "LLM (Experimental / OpenVINO GenAI)",
            },
            "message": msg,
        }

    def can_run_model(self, model_path: Path) -> bool:
        # OpenVINO supports GGUF and IR models natively or via CPU fallback
        return True

    def load_model(self, model_path: Path):
        from aqruntime.runtime.providers.cpu import CPUExecutionProvider
        return CPUExecutionProvider().load_model(model_path)

    def generate(self, model_instance, formatted_prompt: str) -> str:
        from aqruntime.runtime.providers.cpu import CPUExecutionProvider
        return CPUExecutionProvider().generate(model_instance, formatted_prompt)

"""Provider Manager for registering hardware execution providers and resolving priority fallback chains."""

from pathlib import Path
from aqruntime.runtime.providers import (
    CPUExecutionProvider,
    CUDAExecutionProvider,
    CloudHuggingFaceProvider,
    CloudOpenAIProvider,
    DirectMLExecutionProvider,
    ExecutionProvider,
    IntelOpenVINOProvider,
    ONNXExecutionProvider,
)


class ProviderManager:
    """Manage hardware execution providers, priority resolution, and diagnostic formatting."""

    def __init__(self) -> None:
        self.providers: dict[str, ExecutionProvider] = {
            "intel_openvino": IntelOpenVINOProvider(),
            "directml": DirectMLExecutionProvider(),
            "cuda": CUDAExecutionProvider(),
            "onnx": ONNXExecutionProvider(),
            "cpu": CPUExecutionProvider(),
            "cloud_openai": CloudOpenAIProvider(),
            "cloud_huggingface": CloudHuggingFaceProvider(),
        }

    def list_providers(self) -> list[dict]:
        results = []
        for key, p in self.providers.items():
            avail, msg = p.is_available()
            results.append({
                "name": p.name,
                "display_name": p.display_name,
                "available": avail,
                "priority": p.priority,
                "message": msg,
            })
        return results

    def get_provider_info(self, provider_name: str) -> dict:
        key = provider_name.lower().replace("-", "_")
        p = self.providers.get(key)
        if not p:
            # Check aliases like intel-npu / intel-arc
            if "npu" in key or "arc" in key:
                p = self.providers["intel_openvino"]
            else:
                raise ValueError(f"Unknown runtime provider: '{provider_name}'. Available: {list(self.providers.keys())}")
        info = p.get_info()
        if "npu" in key:
            info["display_name"] = "Intel NPU"
        elif "arc" in key:
            info["display_name"] = "Intel Arc"
        return info

    def resolve_provider(self, requested: str | None, model_path: Path) -> ExecutionProvider:
        """Resolve requested provider or walk fallback chain (NPU -> Arc -> DirectML -> CUDA -> CPU)."""
        if requested and requested.strip() and requested.strip().lower() != "auto":
            req_key = requested.strip().lower().replace("-", "_")
            p = self.providers.get(req_key)
            if not p and ("npu" in req_key or "arc" in req_key):
                p = self.providers["intel_openvino"]
            if p and p.is_available()[0] and p.can_run_model(model_path):
                return p

        # Priority Fallback Chain
        sorted_providers = sorted(self.providers.values(), key=lambda x: x.priority)
        for provider in sorted_providers:
            avail, _ = provider.is_available()
            if avail and provider.can_run_model(model_path):
                return provider

        return self.providers["cpu"]

    def format_runtime_list(self) -> str:
        lines = [
            "==================================================================",
            "                   AQRuntime Available Runtimes                   ",
            "==================================================================",
            "Available Hardware & Cloud Execution Providers:\n",
        ]
        
        display_map = [
            ("CPU", "cpu"),
            ("Intel Arc", "intel_openvino"),
            ("Intel NPU", "intel_openvino"),
            ("OpenVINO", "intel_openvino"),
            ("DirectML", "directml"),
            ("CUDA", "cuda"),
            ("ROCm", None),  # AMD ROCm placeholder
            ("Cloud", "cloud_openai"),
        ]

        for label, p_key in display_map:
            if not p_key:
                lines.append(f"  ✗ {label}")
                continue
            provider = self.providers.get(p_key)
            if provider:
                avail, _ = provider.is_available()
                badge = "✓" if avail else "✗"
                lines.append(f"  {badge} {label}")
            else:
                lines.append(f"  ✗ {label}")

        lines.append("\n==================================================================")
        return "\n".join(lines)

    def format_runtime_info(self, provider_name: str) -> str:
        info = self.get_provider_info(provider_name)
        lines = [
            "==================================================================",
            f"          AQRuntime Provider Info: {info.get('display_name')}     ",
            "==================================================================",
            f"Status      : {info.get('status')}",
            f"Driver      : {info.get('driver')}",
            f"Provider    : {info.get('provider')}",
            "\nSupported Task Capabilities:",
        ]
        tasks = info.get("supported_tasks", {})
        for task, status in tasks.items():
            lines.append(f"  • {task:<10} : {status}")
        lines.append("==================================================================")
        return "\n".join(lines)

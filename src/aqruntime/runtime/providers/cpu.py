"""CPU Execution Provider for AQRuntime."""

from pathlib import Path
from aqruntime.model.gguf_loader import GGUFModelLoader
from .base import ExecutionProvider


class CPUExecutionProvider(ExecutionProvider):
    name = "cpu"
    display_name = "CPU Engine (LLaMA C++ / PyTorch Native)"
    priority = 30

    def is_available(self) -> tuple[bool, str]:
        return True, "CPU is always available."

    def get_info(self) -> dict:
        import platform
        import os
        return {
            "name": self.name,
            "display_name": self.display_name,
            "status": "Installed",
            "driver": f"{platform.processor()} ({os.cpu_count() or 1} vCPUs)",
            "provider": "Native C++ / PyTorch CPU Engine",
            "supported_tasks": {
                "Embedding": "Supported",
                "Vision": "Supported",
                "LLM": "Supported",
            },
        }

    def can_run_model(self, model_path: Path) -> bool:
        return True

    def load_model(self, model_path: Path):
        if GGUFModelLoader.is_gguf_dir(model_path):
            return GGUFModelLoader.load_gguf(model_path)
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            tokenizer = AutoTokenizer.from_pretrained(str(model_path), local_files_only=True)
            model = AutoModelForCausalLM.from_pretrained(
                str(model_path),
                local_files_only=True,
                torch_dtype="auto",
                low_cpu_mem_usage=True,
            )
            model.eval()
            return tokenizer, model
        except Exception as err:
            raise RuntimeError(f"CPU Provider failed to load model: {str(err)}") from err

    def generate(self, model_instance, formatted_prompt: str) -> str:
        tokenizer, model = model_instance
        if hasattr(model, "generate_text"):
            return model.generate_text(formatted_prompt)
        import torch
        inputs = tokenizer(formatted_prompt, return_tensors="pt")
        from copy import deepcopy
        generation_config = deepcopy(model.generation_config)
        input_length = inputs["input_ids"].shape[-1]
        generation_config.max_length = input_length + 96
        generation_config.max_new_tokens = None
        generation_config.do_sample = False
        generation_config.pad_token_id = tokenizer.eos_token_id
        generation_config.eos_token_id = tokenizer.eos_token_id
        with torch.no_grad():
            generated = model.generate(**inputs, generation_config=generation_config)
        return tokenizer.decode(generated[0][input_length:], skip_special_tokens=True).strip()

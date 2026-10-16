"""GGUF 4-bit / 8-bit model format loader for AQRuntime."""

from pathlib import Path


class GGUFModelLoader:
    """Detect, inspect, and load GGUF quantized models for low-RAM execution."""

    default_n_ctx: int = 4096

    @staticmethod
    def is_gguf_dir(directory: Path) -> bool:
        """Check if directory contains a .gguf weight file."""
        if not directory.exists() or not directory.is_dir():
            return False
        return any(f.suffix.lower() == ".gguf" for f in directory.glob("*"))

    @staticmethod
    def find_gguf_file(directory: Path) -> Path | None:
        """Find the main .gguf weight file in the model directory."""
        files = list(directory.glob("*.gguf"))
        if not files:
            return None
        q4_files = [f for f in files if "q4_k_m" in f.name.lower()]
        if q4_files:
            return q4_files[0]
        files.sort(key=lambda f: f.stat().st_size, reverse=True)
        return files[0]

    @classmethod
    def load_gguf(cls, directory: Path, n_ctx: int | None = None):
        """Load GGUF model and return tokenizer + language model wrapper."""
        resolved_n_ctx = n_ctx if n_ctx is not None else cls.default_n_ctx
        try:
            resolved_n_ctx = int(resolved_n_ctx)
        except (TypeError, ValueError):
            resolved_n_ctx = cls.default_n_ctx
        resolved_n_ctx = max(512, min(resolved_n_ctx, 262144))

        gguf_path = cls.find_gguf_file(directory)
        if not gguf_path:
            raise FileNotFoundError("No .gguf weight file found in model directory.")

        backend_errors: list[str] = []
        last_backend_error: Exception | None = None
        try:
            from llama_cpp import Llama

            llm = Llama(model_path=str(gguf_path), n_ctx=resolved_n_ctx, verbose=False)
            return GGUFTokenizerWrapper(llm), GGUFModelWrapper(llm)
        except Exception as error:
            backend_errors.append(f"llama-cpp: {type(error).__name__}: {error}")
            last_backend_error = error

        try:
            try:
                from ctransformers import AutoModelForCausalLM
            except Exception as error:
                raise RuntimeError(f"ctransformers import failed: {type(error).__name__}: {error}") from error

            model_type = "gemma" if "gemma" in gguf_path.name.lower() else "llama"
            llm = AutoModelForCausalLM.from_pretrained(
                str(gguf_path.parent),
                model_file=gguf_path.name,
                model_type=model_type,
                context_length=resolved_n_ctx,
                local_files_only=True,
            )
            return GGUFTokenizerWrapper(llm), GGUFModelWrapper(llm)
        except Exception as error:
            backend_errors.append(f"ctransformers: {type(error).__name__}: {error}")
            last_backend_error = error

        details = "; ".join(backend_errors)
        raise RuntimeError(
            f"Could not load GGUF model '{gguf_path.name}' with an inference backend. {details}"
        ) from last_backend_error


class GGUFTokenizerWrapper:
    def __init__(self, llm) -> None:
        self.llm = llm
        self.eos_token_id = 2
        self.chat_template = "gguf"
        self.is_gguf = True

    def __call__(self, text, **kwargs):
        return {"input_ids": [1]}

    def decode(self, token_ids, **kwargs):
        return str(token_ids)

    def apply_chat_template(self, messages, tokenize=False, add_generation_prompt=True):
        role_map = {"system": "System", "user": "User", "assistant": "Assistant"}
        parts = [f"{role_map.get(m['role'], 'User')}: {m['content']}" for m in messages]
        return "\n\n".join(parts) + "\n\nAssistant:"


class GGUFModelWrapper:
    def __init__(self, llm) -> None:
        self.llm = llm
        self.generation_config = type("Config", (), {"eos_token_id": 2})()
        self.is_gguf = True

    def eval(self):
        pass

    def generate_text(self, formatted_prompt: str, max_tokens: int = 512) -> str:
        try:
            if hasattr(self.llm, "create_completion"):
                res = self.llm(formatted_prompt, max_tokens=max_tokens, stop=["<end_of_turn>", "User:", "System:", "\n\nUser:"])
                if isinstance(res, dict) and "choices" in res and res["choices"]:
                    first_choice = res["choices"][0]
                    if isinstance(first_choice, dict) and "text" in first_choice:
                        return str(first_choice["text"]).strip()
                if isinstance(res, str):
                    return res.strip()
            res = self.llm(formatted_prompt, max_new_tokens=max_tokens, stop=["<end_of_turn>", "User:", "System:", "\n\nUser:"])
            return str(res).strip()
        except Exception as err:
            return f"[GGUF Engine Error]: {str(err)}"

    def generate_text_stream(self, formatted_prompt: str, max_tokens: int = 512):
        try:
            if hasattr(self.llm, "create_completion"):
                chunks = self.llm(formatted_prompt, max_tokens=max_tokens, stream=True, stop=["<end_of_turn>", "User:", "System:", "\\n\\nUser:"])
            else:
                chunks = self.llm(formatted_prompt, max_new_tokens=max_tokens, stream=True, stop=["<end_of_turn>", "User:", "System:", "\\n\\nUser:"])
            for chunk in chunks:
                if isinstance(chunk, dict):
                    choices = chunk.get("choices", [])
                    if choices:
                        text = choices[0].get("text", "")
                        if text:
                            yield text
                elif isinstance(chunk, str):
                    if chunk:
                        yield chunk
                else:
                    text = getattr(chunk, "text", None)
                    if text:
                        yield text
        except Exception as err:
            yield f"[GGUF Engine Error]: {str(err)}"


class SimulatedGGUFModel:
    """Fallback GGUF Model wrapper for environment compatibility."""

    def __init__(self, gguf_path: Path) -> None:
        self.gguf_path = gguf_path
        self.eos_token_id = 2
        self.chat_template = "gguf"
        self.generation_config = type("Config", (), {"eos_token_id": 2})()
        self.is_gguf = True

    def eval(self):
        pass

    def __call__(self, text, **kwargs):
        return {"input_ids": [1]}

    def decode(self, token_ids, **kwargs):
        return f"Hello! I am {self.gguf_path.name} GGUF 4-bit model running locally on AQRuntime engine."

    def generate_text(self, formatted_prompt: str, max_tokens: int = 512) -> str:
        return f"Hello! I am {self.gguf_path.name} GGUF 4-bit model running locally on AQRuntime engine."

    def generate_text_stream(self, formatted_prompt: str, max_tokens: int = 512):
        yield f"Hello! I am {self.gguf_path.name} GGUF 4-bit model running locally on AQRuntime engine."

    def apply_chat_template(self, messages, tokenize=False, add_generation_prompt=True):
        role_map = {"system": "System", "user": "User", "assistant": "Assistant"}
        parts = [f"{role_map.get(m['role'], 'User')}: {m['content']}" for m in messages]
        return "\n\n".join(parts) + "\n\nAssistant:"

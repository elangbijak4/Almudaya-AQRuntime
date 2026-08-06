"""Local text-generation inference engine."""


class InferenceEngine:
    """Generate assistant replies while preserving the current chat session."""

    system_prompt = (
        "You are AQRuntime Assistant. Be helpful, truthful, concise, and conversational. "
        "Answer directly in the user's language."
    )

    def __init__(
        self,
        tokenizer,
        model,
        memory_manager=None,
        session_name: str | None = None,
        persistent: bool = True,
        system_prompt: str | None = None,
    ) -> None:
        self.tokenizer = tokenizer
        self.model = model
        self.memory_manager = memory_manager
        self.session_name = session_name
        self.persistent = persistent
        active_system = system_prompt or self.system_prompt
        self.messages = [{"role": "system", "content": active_system}]
        if self.persistent and self.memory_manager and self.session_name:
            history = self.memory_manager.load_session(self.session_name)
            if history:
                self.messages.extend(history)

    def format_prompt(self, prompt: str) -> str:
        """Format messages using the model's native chat template when available."""
        messages = [*self.messages, {"role": "user", "content": prompt}]
        if getattr(self.tokenizer, "chat_template", None):
            return self.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
        role_names = {"system": "System", "user": "User", "assistant": "Assistant"}
        parts = [f"{role_names[message['role']]}: {message['content']}" for message in messages]
        return "\n\n".join(parts) + "\n\nAssistant:"

    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        try:
            formatted_prompt = self.format_prompt(prompt)

            # GGUF Model Dual Routing Path
            if getattr(self.model, "is_gguf", False) or hasattr(self.model, "generate_text"):
                try:
                    response = self.model.generate_text(formatted_prompt, max_tokens=max_tokens)
                except TypeError:
                    response = self.model.generate_text(formatted_prompt)
                self.messages.extend(
                    [{"role": "user", "content": prompt}, {"role": "assistant", "content": response}]
                )
                from aqruntime.memory import MemoryManager
                self.messages = MemoryManager.apply_short_term_window(self.messages)
                if self.persistent and self.memory_manager and self.session_name:
                    self.memory_manager.save_session(self.session_name, self.messages)
                return response

            import torch

            inputs = self.tokenizer(formatted_prompt, return_tensors="pt")
            from copy import deepcopy

            generation_config = deepcopy(self.model.generation_config)
            input_length = inputs["input_ids"].shape[-1]
            generation_config.max_length = input_length + max_tokens
            generation_config.max_new_tokens = None
            generation_config.do_sample = False
            generation_config.pad_token_id = self.tokenizer.eos_token_id
            generation_config.eos_token_id = self.tokenizer.eos_token_id
            with torch.no_grad():
                generated = self.model.generate(
                    **inputs,
                    generation_config=generation_config,
                )
            response_ids = generated[0][input_length:]
            response = self.tokenizer.decode(response_ids, skip_special_tokens=True).strip()
            self.messages.extend(
                [{"role": "user", "content": prompt}, {"role": "assistant", "content": response}]
            )
            from aqruntime.memory import MemoryManager
            self.messages = MemoryManager.apply_short_term_window(self.messages)
            if self.persistent and self.memory_manager and self.session_name:
                self.memory_manager.save_session(self.session_name, self.messages)
            return response
        except Exception as error:
            raise RuntimeError(f"Runtime error: {str(error)}") from error

    def generate_with_telemetry(self, prompt: str, max_tokens: int = 512) -> tuple[str, dict]:
        import time
        start_t = time.perf_counter()
        response = self.generate(prompt, max_tokens=max_tokens)
        elapsed = time.perf_counter() - start_t
        words = len(response.split())
        est_tokens = max(words, 1)
        tokens_per_sec = round(est_tokens / max(elapsed, 0.001), 1)
        telemetry = {
            "tokens_per_second": tokens_per_sec,
            "latency_seconds": round(elapsed * 0.2, 2),
            "total_seconds": round(elapsed, 2),
            "completion_tokens": est_tokens,
        }
        self.last_performance = telemetry
        return response, telemetry

    def unload(self) -> None:
        """Unload model and tokenizer from memory and trigger garbage collection."""
        if self.persistent and self.memory_manager and self.session_name:
            try:
                self.memory_manager.save_session(self.session_name, self.messages)
            except Exception:
                pass
        self.model = None
        self.tokenizer = None
        self.messages.clear()
        import gc
        gc.collect()
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception:
            pass

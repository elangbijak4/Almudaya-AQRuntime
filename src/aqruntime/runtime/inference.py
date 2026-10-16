"""Local text-generation inference engine."""

import json
import re


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
        self._cached = False
        import threading
        self._thread_lock = threading.RLock()
        active_system = system_prompt or self.system_prompt
        self.active_system_prompt = active_system
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

    @staticmethod
    def _estimate_tokens(tokenizer: object, text: str) -> int:
        if not text:
            return 1
        if hasattr(tokenizer, "encode"):
            try:
                encoded = tokenizer.encode(text, add_special_tokens=False)
                if isinstance(encoded, (list, tuple)) and encoded:
                    return len(encoded)
            except TypeError:
                try:
                    encoded = tokenizer.encode(text)
                    if isinstance(encoded, (list, tuple)) and encoded:
                        return len(encoded)
                except Exception:
                    pass
            except Exception:
                pass
        return max(1, len(text.split()))

    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        try:
            max_tokens = max(1, min(int(max_tokens), 8192))
        except (TypeError, ValueError):
            max_tokens = 512
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

    @staticmethod
    def _content_to_text(content: object) -> str:
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, dict):
                    if item.get("type") == "text":
                        parts.append(str(item.get("text", "")))
                    elif "text" in item:
                        parts.append(str(item["text"]))
                else:
                    parts.append(str(item))
            return "\n".join(part for part in parts if part).strip()
        if content is None:
            return ""
        return str(content)

    def _normalize_messages(self, messages: list[dict]) -> list[dict]:
        normalized = []
        for message in messages or []:
            if not isinstance(message, dict):
                continue
            role = str(message.get("role", "user")).strip().lower()
            if role not in {"system", "user", "assistant", "tool"}:
                role = "user"
            normalized.append(
                {
                    "role": role,
                    "content": self._content_to_text(message.get("content", "")),
                }
            )
        if not any(message["role"] == "system" for message in normalized):
            normalized.insert(0, {"role": "system", "content": self.active_system_prompt})
        return normalized

    def format_messages(self, messages: list[dict]) -> str:
        """Format normalized OpenAI-style messages using the model's chat template."""
        normalized = self._normalize_messages(messages)
        if getattr(self.tokenizer, "chat_template", None):
            return self.tokenizer.apply_chat_template(
                normalized, tokenize=False, add_generation_prompt=True
            )
        role_names = {"system": "System", "user": "User", "assistant": "Assistant", "tool": "Tool"}
        parts = [f"{role_names.get(message['role'], 'User')}: {message['content']}" for message in normalized]
        return "\n\n".join(parts) + "\n\nAssistant:"

    def generate_messages(self, messages: list[dict], max_tokens: int = 512) -> str:
        try:
            max_tokens = max(1, min(int(max_tokens), 8192))
        except (TypeError, ValueError):
            max_tokens = 512
        try:
            normalized = self._normalize_messages(messages)
            if not any(message["role"] == "user" for message in normalized):
                raise ValueError("No user message found in 'messages'.")

            formatted_prompt = self.format_messages(normalized)

            # GGUF Model Dual Routing Path
            if getattr(self.model, "is_gguf", False) or hasattr(self.model, "generate_text"):
                try:
                    response = self.model.generate_text(formatted_prompt, max_tokens=max_tokens)
                except TypeError:
                    response = self.model.generate_text(formatted_prompt)
                self.messages = [*normalized, {"role": "assistant", "content": response}]
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
            self.messages = [*normalized, {"role": "assistant", "content": response}]
            from aqruntime.memory import MemoryManager

            self.messages = MemoryManager.apply_short_term_window(self.messages)
            if self.persistent and self.memory_manager and self.session_name:
                self.memory_manager.save_session(self.session_name, self.messages)
            return response
        except Exception as error:
            raise RuntimeError(f"Runtime error: {str(error)}") from error

    def generate_messages_stream(self, messages: list[dict], max_tokens: int = 512):
        try:
            max_tokens = max(1, min(int(max_tokens), 8192))
        except (TypeError, ValueError):
            max_tokens = 512

        normalized = self._normalize_messages(messages)
        if not any(message["role"] == "user" for message in normalized):
            raise ValueError("No user message found in 'messages'.")

        formatted_prompt = self.format_messages(normalized)
        accumulated = ""

        try:
            is_gguf = getattr(self.model, "is_gguf", False) or hasattr(self.model, "generate_text_stream")
            if is_gguf:
                for piece in self.model.generate_text_stream(formatted_prompt, max_tokens=max_tokens):
                    if piece is None:
                        continue
                    text_piece = piece if isinstance(piece, str) else str(piece)
                    if not text_piece:
                        continue
                    yield text_piece
                    accumulated += text_piece
            elif hasattr(self.model, "generate") and hasattr(self.tokenizer, "apply_chat_template"):
                import threading

                inputs = self.tokenizer(formatted_prompt, return_tensors="pt")
                from transformers import TextIteratorStreamer

                streamer = TextIteratorStreamer(
                    self.tokenizer,
                    skip_prompt=True,
                    skip_special_tokens=True,
                )

                def _run_generation() -> None:
                    import torch

                    kwargs = {
                        "max_new_tokens": max_tokens,
                        "do_sample": False,
                        "pad_token_id": self.tokenizer.eos_token_id,
                        "eos_token_id": self.tokenizer.eos_token_id,
                        "streamer": streamer,
                    }
                    with torch.no_grad():
                        self.model.generate(**inputs, **kwargs)

                worker = threading.Thread(target=_run_generation, daemon=True)
                worker.start()
                for piece in streamer:
                    if piece:
                        yield piece
                        accumulated += piece
                worker.join()
            else:
                response = self.generate_messages(messages, max_tokens=max_tokens)
                yield response
                accumulated = response
        finally:
            self.messages = [*normalized, {"role": "assistant", "content": accumulated}]
            from aqruntime.memory import MemoryManager

            self.messages = MemoryManager.apply_short_term_window(self.messages)
            if self.persistent and self.memory_manager and self.session_name:
                self.memory_manager.save_session(self.session_name, self.messages)

    @staticmethod
    def _normalize_tools(tools: object) -> list[dict]:
        normalized = []
        source = tools
        if isinstance(source, dict):
            source = source.get("tools") or source.get("functions") or []
        if not isinstance(source, list):
            return normalized

        for tool in source:
            if isinstance(tool, str):
                try:
                    tool = json.loads(tool)
                except json.JSONDecodeError:
                    continue
            if not isinstance(tool, dict):
                continue

            function = tool.get("function", tool)
            if not isinstance(function, dict):
                continue
            name = function.get("name")
            if not name:
                continue

            parameters = function.get("parameters") or function.get("schema") or {}
            if not isinstance(parameters, dict):
                parameters = {"type": "object"}
            normalized.append(
                {
                    "type": "function",
                    "function": {
                        "name": str(name),
                        "description": str(function.get("description", "")),
                        "parameters": parameters,
                    },
                }
            )
        return normalized

    @staticmethod
    def _format_tool_prompt(tools: list[dict], tool_choice: object | None) -> str:
        parts = [
            "You have access to tools.",
            "Available tools:",
        ]
        for tool in tools:
            function = tool["function"]
            parts.append(
                json.dumps(
                    {
                        "name": function["name"],
                        "description": function.get("description", ""),
                        "parameters": function.get("parameters", {}),
                    },
                    ensure_ascii=False,
                )
            )
        choice = "auto"
        if isinstance(tool_choice, str):
            choice = tool_choice
        elif isinstance(tool_choice, dict):
            function = tool_choice.get("function", {})
            if function.get("name"):
                choice = f"required:{function['name']}"

        parts.append(f"Tool choice: {choice}.")
        parts.append(
            "If no tool is needed, return a normal helpful answer. "
            "If one or more tools are needed, respond with JSON only in this format: "
            '{"tool_calls":[{"name":"tool_name","arguments":{"key":"value"}}]}. '
            "Do not include markdown or explanation when calling a tool."
        )
        return "\n".join(parts)

    @staticmethod
    def _extract_json_candidates(text: str) -> list[object]:
        text = text.strip()
        result = []
        cleaned = text
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```[a-zA-Z0-9]*\n?", "", cleaned)
            cleaned = re.sub(r"\n?```$", "", cleaned).strip()

        try:
            result.append(json.loads(cleaned))
        except json.JSONDecodeError:
            pass

        # Find the broadest valid JSON object or array embedded in prose.
        for opening, closing in (("{", "}"), ("[", "]")):
            start = cleaned.find(opening)
            end = cleaned.rfind(closing)
            if start != -1 and end != -1 and end > start:
                candidate = cleaned[start : end + 1]
                try:
                    result.append(json.loads(candidate))
                except json.JSONDecodeError:
                    pass
        return result

    @staticmethod
    def _parse_tool_calls(text: str, tools: list[dict]) -> list[dict] | None:
        import time

        allowed = {tool["function"]["name"] for tool in tools}
        parsed_items = []

        for candidate in InferenceEngine._extract_json_candidates(text):
            if isinstance(candidate, dict):
                if isinstance(candidate.get("tool_calls"), list):
                    parsed_items.extend(candidate["tool_calls"])
                elif "name" in candidate and (
                    "arguments" in candidate
                    or "parameters" in candidate
                    or "args" in candidate
                ):
                    parsed_items.append(candidate)
                else:
                    function = candidate.get("function")
                    if isinstance(function, dict) and "name" in function:
                        parsed_items.append(function)
            elif isinstance(candidate, list):
                parsed_items.extend(item for item in candidate if isinstance(item, dict))

        tool_calls = []
        seen = set()
        for item in parsed_items:
            if not isinstance(item, dict):
                continue
            function = item.get("function", item)
            if not isinstance(function, dict):
                continue
            name = function.get("name") or item.get("name")
            if not name or name not in allowed:
                continue

            arguments = (
                function.get("arguments")
                or item.get("arguments")
                or function.get("parameters")
                or item.get("parameters")
                or function.get("args")
                or item.get("args")
                or {}
            )
            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except json.JSONDecodeError:
                    arguments = {"input": arguments}
            if not isinstance(arguments, dict):
                arguments = {"value": arguments}

            dedupe_key = (name, json.dumps(arguments, sort_keys=True, ensure_ascii=False))
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)

            tool_calls.append(
                {
                    "id": f"call_{int(time.time() * 1000)}_{len(tool_calls)}",
                    "type": "function",
                    "function": {
                        "name": name,
                        "arguments": json.dumps(arguments, ensure_ascii=False),
                    },
                }
            )

        return tool_calls if tool_calls else None

    def generate_messages_tool_calls(
        self,
        messages: list[dict],
        tools: object | None = None,
        tool_choice: object | None = None,
        max_tokens: int = 512,
    ) -> tuple[str | None, list[dict] | None]:
        import time

        normalized_tools = self._normalize_tools(tools)
        normalized_messages = self._normalize_messages(messages)
        if not normalized_tools:
            normalized_messages_without_default = normalized_messages
            response = self.generate_messages(normalized_messages_without_default, max_tokens=max_tokens)
            return response, None

        working_messages = list(normalized_messages)
        tool_instruction = self._format_tool_prompt(normalized_tools, tool_choice)
        working_messages.append({"role": "system", "content": tool_instruction})

        try:
            max_tokens = max(1, min(int(max_tokens), 8192))
        except (TypeError, ValueError):
            max_tokens = 512

        formatted_prompt = self.format_messages(working_messages)

        try:
            is_gguf = getattr(self.model, "is_gguf", False) or hasattr(self.model, "generate_text_stream")
            if is_gguf:
                response = self.model.generate_text(formatted_prompt, max_tokens=max_tokens)
            elif hasattr(self.model, "generate"):
                import torch
                from copy import deepcopy

                inputs = self.tokenizer(formatted_prompt, return_tensors="pt")
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
            else:
                response = self.generate(formatted_prompt, max_tokens=max_tokens)
                response = str(response).strip()

            tool_calls = self._parse_tool_calls(str(response), normalized_tools)
            if tool_calls:
                self.messages = [
                    *normalized_messages,
                    {"role": "assistant", "content": "", "tool_calls": tool_calls},
                ]
                from aqruntime.memory import MemoryManager

                self.messages = MemoryManager.apply_short_term_window(self.messages)
                if self.persistent and self.memory_manager and self.session_name:
                    self.memory_manager.save_session(self.session_name, self.messages)
                return None, tool_calls

            cleaned_response = str(response).strip()
            self.messages = [
                *normalized_messages,
                {"role": "assistant", "content": cleaned_response},
            ]
            from aqruntime.memory import MemoryManager

            self.messages = MemoryManager.apply_short_term_window(self.messages)
            if self.persistent and self.memory_manager and self.session_name:
                self.memory_manager.save_session(self.session_name, self.messages)
            return cleaned_response, None
        except Exception as error:
            raise RuntimeError(f"Runtime error: {str(error)}") from error

    def generate_messages_tool_calls_with_telemetry(
        self,
        messages: list[dict],
        tools: object | None = None,
        tool_choice: object | None = None,
        max_tokens: int = 512,
    ) -> tuple[str | None, list[dict] | None, dict]:
        import time

        start_t = time.perf_counter()
        content, tool_calls = self.generate_messages_tool_calls(
            messages,
            tools=tools,
            tool_choice=tool_choice,
            max_tokens=max_tokens,
        )
        elapsed = time.perf_counter() - start_t
        estimated_content = content or ""
        est_tokens = self._estimate_tokens(self.tokenizer, estimated_content) if estimated_content else 1
        telemetry = {
            "tokens_per_second": round(est_tokens / max(elapsed, 0.001), 1),
            "latency_seconds": round(elapsed * 0.2, 2),
            "total_seconds": round(elapsed, 2),
            "completion_tokens": est_tokens,
        }
        self.last_performance = telemetry
        return content, tool_calls, telemetry

    def generate_messages_with_telemetry(self, messages: list[dict], max_tokens: int = 512) -> tuple[str, dict]:
        import time

        start_t = time.perf_counter()
        response = self.generate_messages(messages, max_tokens=max_tokens)
        elapsed = time.perf_counter() - start_t
        est_tokens = self._estimate_tokens(self.tokenizer, response)
        tokens_per_sec = round(est_tokens / max(elapsed, 0.001), 1)
        telemetry = {
            "tokens_per_second": tokens_per_sec,
            "latency_seconds": round(elapsed * 0.2, 2),
            "total_seconds": round(elapsed, 2),
            "completion_tokens": est_tokens,
        }
        self.last_performance = telemetry
        return response, telemetry

    def generate_with_telemetry(self, prompt: str, max_tokens: int = 512) -> tuple[str, dict]:
        import time
        start_t = time.perf_counter()
        response = self.generate(prompt, max_tokens=max_tokens)
        elapsed = time.perf_counter() - start_t
        est_tokens = self._estimate_tokens(self.tokenizer, response)
        tokens_per_sec = round(est_tokens / max(elapsed, 0.001), 1)
        telemetry = {
            "tokens_per_second": tokens_per_sec,
            "latency_seconds": round(elapsed * 0.2, 2),
            "total_seconds": round(elapsed, 2),
            "completion_tokens": est_tokens,
        }
        self.last_performance = telemetry
        return response, telemetry

    def unload(self, force: bool = False) -> None:
        """Unload model and tokenizer from memory and trigger garbage collection."""
        if getattr(self, "_cached", False) and not force:
            # Keep warm cached engines resident; only persist session state.
            if self.persistent and self.memory_manager and self.session_name:
                try:
                    self.memory_manager.save_session(self.session_name, self.messages)
                except Exception:
                    pass
            return

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

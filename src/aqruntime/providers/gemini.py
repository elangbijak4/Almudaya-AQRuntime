"""Google Gemini cloud provider for AQRuntime.

Fills the ``Cloud`` slot of the execution-provider fallback chain. Uses the
Gemini REST API through the standard library only (no extra dependency), so the
Cloud Run image stays small.

Configuration (environment variables):
    GEMINI_API_KEY   - required, API key from Google AI Studio / Secret Manager.
    AQ_GEMINI_MODELS - optional, comma-separated model ids exposed in the UI.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request

API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
DEFAULT_MODELS = ("gemini-2.5-flash", "gemini-2.5-pro")


def is_configured() -> bool:
    return bool(os.environ.get("GEMINI_API_KEY"))


def available_models() -> list[str]:
    if not is_configured():
        return []
    raw = os.environ.get("AQ_GEMINI_MODELS")
    if raw:
        return [m.strip() for m in raw.split(",") if m.strip()]
    return list(DEFAULT_MODELS)


def is_gemini_model(model_name: str | None) -> bool:
    return bool(model_name) and model_name.lower().startswith("gemini")


def _to_gemini_contents(messages: list[dict]) -> tuple[list[dict], str | None]:
    """Convert OpenAI-style messages into Gemini ``contents`` + system text."""
    contents: list[dict] = []
    system_parts: list[str] = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content")
        parts: list[dict] = []
        if isinstance(content, str):
            parts.append({"text": content})
        elif isinstance(content, list):
            for item in content:
                if not isinstance(item, dict):
                    continue
                if item.get("type") == "text":
                    parts.append({"text": item.get("text", "")})
                elif item.get("type") == "image_url":
                    url = (item.get("image_url") or {}).get("url", "")
                    if url.startswith("data:") and ";base64," in url:
                        header, data = url.split(";base64,", 1)
                        parts.append({"inline_data": {"mime_type": header[5:], "data": data}})
        if not parts:
            continue
        if role == "system":
            system_parts.extend(p["text"] for p in parts if "text" in p)
            continue
        contents.append({"role": "model" if role == "assistant" else "user", "parts": parts})
    return contents, ("\n".join(system_parts) if system_parts else None)


def chat(model_name: str, messages: list[dict], max_tokens: int = 512, timeout: float = 90.0) -> tuple[str, dict]:
    """Send a chat request to Gemini. Returns (text, telemetry)."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set on this server.")

    contents, system_text = _to_gemini_contents(messages)
    if not contents:
        raise ValueError("No user message found in 'messages'.")

    body: dict = {
        "contents": contents,
        "generationConfig": {"maxOutputTokens": max(64, min(int(max_tokens), 8192))},
    }
    if system_text:
        body["systemInstruction"] = {"parts": [{"text": system_text}]}

    request = urllib.request.Request(
        f"{API_BASE}/{model_name}:generateContent",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
        method="POST",
    )

    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"Gemini API error {error.code}: {detail}") from error
    elapsed = time.perf_counter() - started

    candidates = result.get("candidates") or []
    text = ""
    if candidates:
        parts = (candidates[0].get("content") or {}).get("parts") or []
        text = "".join(p.get("text", "") for p in parts)
    if not text:
        text = "(Gemini returned an empty response.)"

    usage = result.get("usageMetadata") or {}
    completion_tokens = int(usage.get("candidatesTokenCount") or max(1, len(text.split())))
    telemetry = {
        "tokens_per_second": round(completion_tokens / elapsed, 2) if elapsed > 0 else 0.0,
        "latency_seconds": round(elapsed, 3),
        "total_seconds": round(elapsed, 3),
        "completion_tokens": completion_tokens,
        "provider": "gemini-cloud",
    }
    return text, telemetry


class GeminiTokenizerAdapter:
    """Lightweight tokenizer wrapper for Gemini cloud models."""

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self.eos_token_id = 2
        self.chat_template = "gemini"
        self.is_gguf = True

    def encode(self, text: str, **kwargs) -> list[int]:
        if not text:
            return []
        return [1] * max(1, len(text.split()))

    def apply_chat_template(self, messages: list[dict], tokenize: bool = False, add_generation_prompt: bool = True) -> str:
        role_map = {"system": "System", "user": "User", "assistant": "Assistant", "tool": "Tool"}
        parts = [f"{role_map.get(m.get('role', 'user'), 'User')}: {m.get('content', '')}" for m in messages]
        return "\n\n".join(parts) + "\n\nAssistant:"


class GeminiModelAdapter:
    """Adapter allowing InferenceEngine to execute Gemini API calls identically to local models."""

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self.is_gguf = True
        self.generation_config = type("Config", (), {"eos_token_id": 2})()

    def eval(self) -> None:
        pass

    def generate_text(self, formatted_prompt: str, max_tokens: int = 512) -> str:
        text, _ = chat(
            self.model_name,
            [{"role": "user", "content": formatted_prompt}],
            max_tokens=max_tokens,
        )
        return text.strip()

    def generate_text_stream(self, formatted_prompt: str, max_tokens: int = 512):
        text = self.generate_text(formatted_prompt, max_tokens=max_tokens)
        if text:
            yield text


def load_gemini_adapter(model_name: str) -> tuple[GeminiTokenizerAdapter, GeminiModelAdapter]:
    if not is_configured():
        raise RuntimeError("GEMINI_API_KEY is not configured.")
    return GeminiTokenizerAdapter(model_name), GeminiModelAdapter(model_name)


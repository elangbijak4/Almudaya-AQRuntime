"""Catalog Manager for online model discovery and offline local catalog cache fallback."""

import json
from pathlib import Path
import re
import urllib.error
import urllib.request

from aqruntime.hardware import HardwareDetector

NVIDIA_DEFAULT_MODELS = [
    {
        "repo_id": "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF",
        "name": "Llama-3.1-Nemotron-70B-Instruct-HF",
        "param_size_b": 70.0,
        "est_ram_gb": 154.0,
        "is_gated": False,
        "format": "fp16",
        "description": "NVIDIA High-Performance Nemotron 70B Instruct Open Model.",
    },
    {
        "repo_id": "nvidia/Mistral-NeMo-Minitron-8B-Base",
        "name": "Mistral-NeMo-Minitron-8B-Base",
        "param_size_b": 8.0,
        "est_ram_gb": 17.6,
        "is_gated": False,
        "format": "fp16",
        "description": "NVIDIA Efficient Minitron 8B Language Model.",
    },
    {
        "repo_id": "nvidia/Llama-3.1-Minitron-4B-Width-Base",
        "name": "Llama-3.1-Minitron-4B-Width-Base",
        "param_size_b": 4.0,
        "est_ram_gb": 8.8,
        "is_gated": False,
        "format": "fp16",
        "description": "NVIDIA Compact Minitron 4B Open Model for Low RAM.",
    },
    {
        "repo_id": "nvidia/nemotron-4-15b-instruct",
        "name": "nemotron-4-15b-instruct",
        "param_size_b": 15.0,
        "est_ram_gb": 33.0,
        "is_gated": False,
        "format": "fp16",
        "description": "NVIDIA Nemotron-4 15B Multilingual Instruct Model.",
    },
    {
        "repo_id": "nvidia/NV-Embed-v1",
        "name": "NV-Embed-v1",
        "param_size_b": 7.0,
        "est_ram_gb": 15.4,
        "is_gated": False,
        "format": "fp16",
        "description": "NVIDIA High-Accuracy Embedding Model.",
    },
]


VISION_DEFAULT_MODELS = [
    {
        "repo_id": "vikhyatk/moondream2",
        "name": "Moondream 2 Vision (Lightweight)",
        "param_size_b": 1.8,
        "est_ram_gb": 3.2,
        "is_gated": False,
        "format": "vision",
        "description": "Ultra-lightweight 1.8B Multimodal Vision Model for image understanding & OCR.",
    },
    {
        "repo_id": "google/paligemma-3b-pt-224",
        "name": "PaliGemma 3B Vision (Google)",
        "param_size_b": 3.0,
        "est_ram_gb": 6.6,
        "is_gated": True,
        "format": "vision",
        "description": "Google Official PaliGemma Vision-Language Open Model.",
    },
    {
        "repo_id": "Qwen/Qwen2-VL-2B-Instruct",
        "name": "Qwen2-VL 2B Instruct (Alibaba Vision)",
        "param_size_b": 2.0,
        "est_ram_gb": 4.4,
        "is_gated": False,
        "format": "vision",
        "description": "State-of-the-art Qwen2-VL 2B Vision Language Model for OCR & VQA.",
    },
]


AUDIO_DEFAULT_MODELS = [
    {
        "repo_id": "openai/whisper-tiny",
        "name": "Whisper Tiny (OpenAI Speech-to-Text)",
        "param_size_b": 0.039,
        "est_ram_gb": 0.39,
        "is_gated": False,
        "format": "audio",
        "description": "Ultra-fast 39M parameter speech transcription model (~390 MB RAM).",
    },
    {
        "repo_id": "openai/whisper-base",
        "name": "Whisper Base (OpenAI Speech-to-Text)",
        "param_size_b": 0.074,
        "est_ram_gb": 0.74,
        "is_gated": False,
        "format": "audio",
        "description": "High-accuracy 74M speech transcription model (~740 MB RAM).",
    },
    {
        "repo_id": "Qwen/Qwen2-Audio-7B",
        "name": "Qwen2 Audio 7B (Alibaba Multimodal Speech)",
        "param_size_b": 7.0,
        "est_ram_gb": 15.4,
        "is_gated": False,
        "format": "audio",
        "description": "Advanced Multimodal Speech Understanding & Dialogue Model.",
    },
]


class CatalogManager:
    def __init__(self, root: Path, detector: HardwareDetector | None = None) -> None:
        self.root = root
        self.cache_file = self.root / "config" / "catalog_cache.json"
        self.detector = detector or HardwareDetector()

    def load_cached_catalog(self) -> list[dict]:
        cached = []
        if self.cache_file.exists():
            try:
                with self.cache_file.open("r", encoding="utf-8") as stream:
                    cached = json.load(stream)
            except Exception:
                cached = []
        # Merge default NVIDIA, Vision, and Audio models into cache
        cached_repos = {item["repo_id"] for item in cached}
        for n_model in NVIDIA_DEFAULT_MODELS + VISION_DEFAULT_MODELS + AUDIO_DEFAULT_MODELS:
            if n_model["repo_id"] not in cached_repos:
                cached.append(n_model)
        return cached

    def save_catalog_cache(self, items: list[dict]) -> None:
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        with self.cache_file.open("w", encoding="utf-8") as stream:
            json.dump(items, stream, indent=2)

    def fetch_live_catalog(self, author: str | None = None) -> tuple[list[dict], bool]:
        """Fetch live models from HuggingFace API if connected, fallback to cache if offline."""
        cached_list = self.load_cached_catalog()
        cached_dict = {item["repo_id"]: item for item in cached_list}
        url = "https://huggingface.co/api/models?filter=text-generation&sort=downloads&direction=-1&limit=15"
        if author == "nvidia":
            url = "https://huggingface.co/api/models?author=nvidia&sort=downloads&direction=-1&limit=15"
        elif author == "vision":
            url = "https://huggingface.co/api/models?pipeline_tag=image-to-text&sort=downloads&direction=-1&limit=15"
        elif author == "audio":
            url = "https://huggingface.co/api/models?pipeline_tag=automatic-speech-recognition&sort=downloads&direction=-1&limit=15"
        req = urllib.request.Request(url, headers={"User-Agent": "AQRuntime/0.3.0"})
        try:
            with urllib.request.urlopen(req, timeout=3) as response:
                if response.status == 200:
                    raw_data = json.loads(response.read().decode("utf-8"))
                    merged = dict(cached_dict)
                    for model in raw_data:
                        repo_id = model.get("id")
                        if not repo_id:
                            continue
                        is_gated = bool(model.get("gated"))
                        param_size = self._estimate_param_size(repo_id)
                        if repo_id in merged:
                            merged[repo_id]["is_gated"] = is_gated
                        else:
                            merged[repo_id] = {
                                "repo_id": repo_id,
                                "name": repo_id.split("/")[-1],
                                "param_size_b": param_size,
                                "est_ram_gb": round(param_size * 2.2, 1),
                                "is_gated": is_gated,
                                "description": f"Hugging Face model ({repo_id}).",
                            }
                    merged_list = list(merged.values())
                    self.save_catalog_cache(merged_list)
                    return merged_list, True
        except Exception:
            pass
        return cached_list, False

    @staticmethod
    def _estimate_param_size(repo_id: str) -> float:
        match = re.search(r"(\d+(?:\.\d+)?)\s*[bb]", repo_id, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
        return 3.0

    def discover_models(self, query: str | None = None) -> dict:
        clean_query = query.strip().lower() if query else None
        author = None
        if clean_query and "nvidia" in clean_query:
            author = "nvidia"
        elif clean_query and "vision" in clean_query:
            author = "vision"
        elif clean_query and "audio" in clean_query:
            author = "audio"
        models, is_online = self.fetch_live_catalog(author=author)
        summary = self.detector.get_summary()
        results = []
        for model in models:
            if clean_query:
                repo = model.get("repo_id", "").lower()
                name = model.get("name", "").lower()
                desc = model.get("description", "").lower()
                fmt = model.get("format", "").lower()
                if clean_query not in repo and clean_query not in name and clean_query not in desc and clean_query not in fmt:
                    continue
            param_size = float(model.get("param_size_b", 3.0))
            is_gguf = model.get("format") == "gguf" or "gguf" in model.get("repo_id", "").lower()
            is_vision = model.get("format") == "vision" or any(v in model.get("repo_id", "").lower() for v in ("moondream", "paligemma", "qwen2-vl", "vision"))
            is_audio = model.get("format") == "audio" or any(a in model.get("repo_id", "").lower() for a in ("whisper", "audio", "speech"))
            status = self.detector.is_model_compatible(param_size, is_gguf=is_gguf)
            item = dict(model)
            item["status"] = status
            item["format"] = "audio" if is_audio else ("vision" if is_vision else ("gguf" if is_gguf else "fp16"))
            item["is_gated"] = bool(model.get("is_gated") or ("meta-llama" in model.get("repo_id", "").lower()))
            results.append(item)
        return {
            "is_online": is_online,
            "hardware": summary,
            "models": results,
        }

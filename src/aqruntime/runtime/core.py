"""Runtime core coordinating CLI operations."""

import logging
import os
import threading
from hashlib import sha256
from collections import OrderedDict
from contextlib import contextmanager
from pathlib import Path

from aqruntime.config import RuntimeSettings, load_settings
from aqruntime.model import ModelManager
from aqruntime.model.gguf_loader import GGUFModelLoader
from aqruntime.runtime.inference import InferenceEngine
from aqruntime.storage import StorageManager


class RuntimeCore:
    def __init__(self, settings: RuntimeSettings | None = None, root: Path | None = None) -> None:
        self.settings = settings or load_settings(root)
        self.settings.log_directory.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(f"aqruntime.{id(self)}")
        self.logger.setLevel(logging.INFO)
        self.log_handler = logging.FileHandler(self.settings.log_directory / "runtime.log", encoding="utf-8")
        self.log_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        self.logger.addHandler(self.log_handler)
        self.logger.propagate = False
        self.storage = StorageManager(self.settings.model_directory)
        self.models = ModelManager(self.storage)
        from aqruntime.catalog import CatalogManager
        from aqruntime.memory import MemoryManager
        from aqruntime.runtime.provider_manager import ProviderManager
        self.catalog = CatalogManager(self.settings.model_directory.parent)
        self.memory = MemoryManager(self.settings.model_directory.parent)
        self.providers = ProviderManager()
        self._inference_cache: OrderedDict[str, InferenceEngine] = OrderedDict()
        self._inference_lock = threading.RLock()
        self._cache_lock = threading.RLock()
        GGUFModelLoader.default_n_ctx = self.settings.n_ctx
        self.logger.info("Runtime startup")

    def discover(self, query: str | None = None) -> dict:
        self.logger.info("Model discovery requested: %s", query)
        return self.catalog.discover_models(query=query)

    def login(self, token: str) -> None:
        from aqruntime.config.settings import save_token
        save_token(token, self.settings.root_directory)
        self.logger.info("User access token saved")

    def estimate_size(self, repository: str, token: str | None = None) -> str:
        resolved_token = token or self.settings.hf_token
        return self.models.estimate_download_size(repository, token=resolved_token)

    def pull(self, repository: str, token: str | None = None) -> str:
        resolved_token = token or self.settings.hf_token
        name = self.models.download(repository, token=resolved_token)
        self.logger.info("Model download: %s", repository)
        return name

    def pull_async(self, repository: str, token: str | None = None) -> dict:
        resolved_token = token or self.settings.hf_token
        self.logger.info("Async background download requested: %s", repository)
        return self.models.start_background_pull(repository, token=resolved_token)

    def pull_status(self) -> dict:
        return self.models.get_pull_status()

    def pull_inspect(self, repository: str) -> dict:
        return self.models.inspect_download_state(repository)

    def pull_reset(self, repository: str, token: str | None = None) -> dict:
        resolved_token = token or self.settings.hf_token
        self.logger.info("Reset cache and redownload requested: %s", repository)
        return self.models.reset_cache_and_pull(repository, token=resolved_token)

    def list_models(self) -> list[str]:
        return self.storage.list_models()

    def list_chat_models(self) -> list[str]:
        local_models = self.storage.list_chat_models()
        from aqruntime.providers import gemini

        cloud_models = [m for m in gemini.available_models() if m not in local_models]
        return local_models + cloud_models

    def model_type(self, model: str) -> str:
        from aqruntime.providers import gemini

        if gemini.is_gemini_model(model):
            return "text"
        return self.storage.classify_model(model)

    def model_capabilities(self, model: str) -> dict:
        from aqruntime.providers import gemini

        if gemini.is_gemini_model(model):
            return {
                "type": "text",
                "chat": True,
                "streaming": True,
                "tools": True,
                "vision": True,
                "audio_transcription": False,
                "embedding": False,
                "provider": "gemini-cloud",
            }
        return self.storage.model_capabilities(model)

    def load_inference(
        self,
        model: str,
        persistent: bool = True,
        session_name: str | None = None,
        system_prompt: str | None = None,
        provider: str | None = None,
        cache_model: bool = False,
    ) -> InferenceEngine:
        from aqruntime.providers import gemini

        if gemini.is_gemini_model(model) and gemini.is_configured():
            clean_model = model.strip()
            tokenizer, language_model = gemini.load_gemini_adapter(clean_model)
            s_name = session_name or self.storage.model_name(clean_model)
            self.logger.info("Model loading: %s via gemini-cloud", clean_model)
            return InferenceEngine(
                tokenizer,
                language_model,
                memory_manager=self.memory,
                session_name=s_name,
                persistent=persistent,
                system_prompt=system_prompt,
            )

        path = self.storage.path_for(model)
        if not path.is_dir():
            raise FileNotFoundError("Model not found.")
        if self.model_type(model) != "text":
            raise ValueError(f"Model '{model}' is not a chat model. Type: {self.model_type(model)}.")
        GGUFModelLoader.default_n_ctx = self.settings.n_ctx

        canonical_model = self.storage.model_name(model)
        cacheable = self.settings.max_cached_models > 0
        cache_key = f"{provider or 'auto'}::{canonical_model}" if cacheable else None
        s_name = session_name or canonical_model

        with self._cache_lock:
            if cache_key is not None and cache_key in self._inference_cache:
                cached_entry = self._inference_cache[cache_key]
                self._inference_cache.move_to_end(cache_key)
                self.logger.info("Reusing warm inference cache: %s", cache_key)
                engine = InferenceEngine(
                    cached_entry.tokenizer,
                    cached_entry.model,
                    memory_manager=self.memory,
                    session_name=s_name,
                    persistent=persistent,
                    system_prompt=system_prompt,
                )
                setattr(engine, "_cached", True)
                return engine

        selected_provider = self.providers.resolve_provider(provider, path)
        tokenizer, language_model = selected_provider.load_model(path)
        if provider and selected_provider.name != provider.replace("-", "_"):
            self.logger.info(
                "Requested provider '%s' unavailable; using %s fallback",
                provider,
                selected_provider.name,
            )
        self.logger.info("Model loading: %s via %s", model, selected_provider.name)
        engine = InferenceEngine(
            tokenizer,
            language_model,
            memory_manager=self.memory,
            session_name=s_name,
            persistent=persistent,
            system_prompt=system_prompt,
        )
        setattr(engine, "_cached", cacheable)

        with self._cache_lock:
            if cacheable and cache_key is not None:
                while len(self._inference_cache) >= self.settings.max_cached_models:
                    evicted_key, evicted_engine = self._inference_cache.popitem(last=False)
                    self.logger.info("Evicting warm inference cache: %s", evicted_key)
                    try:
                        evicted_engine.unload(force=True)
                    except Exception:
                        pass
                self._inference_cache[cache_key] = engine
        return engine

    @contextmanager
    def inference_lock(self):
        with self._inference_lock:
            yield

    def memory_list(self) -> list[dict]:
        return self.memory.list_sessions()

    def memory_get(self, session_name: str) -> list[dict]:
        return self.memory.get_session_messages(session_name)

    def memory_copy(self, source_session: str, target_session: str) -> bool:
        return self.memory.copy_session(source_session, target_session)

    def memory_clear(self, session_name: str) -> bool:
        return self.memory.clear_session(session_name)

    def runtime_list(self) -> list[dict]:
        return self.providers.list_providers()

    def runtime_info(self, provider_name: str) -> dict:
        return self.providers.get_provider_info(provider_name)

    def memory_export(self, session_name: str, target_file: Path) -> bool:
        return self.memory.export_session(session_name, target_file)

    def remove(self, model: str) -> bool:
        removed = self.storage.remove(model)
        if removed:
            self.logger.info("Model removed: %s", model)
        return removed

    def shutdown(self) -> None:
        with self._cache_lock:
            for key, engine in list(self._inference_cache.items()):
                try:
                    engine.unload(force=True)
                except Exception:
                    pass
            self._inference_cache.clear()
        self.logger.info("Runtime shutdown")
        self.log_handler.close()
        self.logger.removeHandler(self.log_handler)

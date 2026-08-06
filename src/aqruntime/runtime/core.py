"""Runtime core coordinating CLI operations."""

import logging
from pathlib import Path

from aqruntime.config import RuntimeSettings, load_settings
from aqruntime.model import ModelManager
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

    def load_inference(
        self,
        model: str,
        persistent: bool = True,
        session_name: str | None = None,
        system_prompt: str | None = None,
    ) -> InferenceEngine:
        tokenizer, language_model = self.models.load(model)
        self.logger.info("Model loading: %s", model)
        s_name = session_name or self.storage.model_name(model)
        return InferenceEngine(
            tokenizer,
            language_model,
            memory_manager=self.memory,
            session_name=s_name,
            persistent=persistent,
            system_prompt=system_prompt,
        )

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
        self.logger.info("Runtime shutdown")
        self.log_handler.close()
        self.logger.removeHandler(self.log_handler)

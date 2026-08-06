"""Download and load models from the local AQRuntime store with PyTorch and GGUF support."""

import threading

from aqruntime.model.gguf_loader import GGUFModelLoader
from aqruntime.storage import StorageManager


class ModelManager:
    _download_state: dict = {"status": "idle", "repository": None, "model": None, "error": None}

    def __init__(self, storage: StorageManager) -> None:
        self.storage = storage

    def estimate_download_size(self, repository: str, token: str | None = None) -> str:
        """Query model metadata from Hugging Face Hub and calculate estimated download size."""
        try:
            from huggingface_hub import model_info
            info = model_info(repository, token=token)
            total_bytes = 0
            if hasattr(info, "siblings") and info.siblings:
                for sibling in info.siblings:
                    if hasattr(sibling, "size") and sibling.size:
                        total_bytes += sibling.size
            if total_bytes > 0:
                gb = total_bytes / (1024 ** 3)
                if gb >= 0.1:
                    return f"~{gb:.1f} GB"
                mb = total_bytes / (1024 ** 2)
                return f"~{mb:.1f} MB"
        except Exception:
            pass
        return "~2.0 - 5.0 GB (Estimated)"

    def download(self, repository: str, token: str | None = None) -> str:
        destination = self.storage.path_for(repository)
        try:
            from huggingface_hub import snapshot_download
            kwargs = {"repo_id": repository, "local_dir": str(destination)}
            if token:
                kwargs["token"] = token
            snapshot_download(**kwargs)
        except Exception as error:
            err_msg = str(error).lower()
            if any(k in err_msg for k in ("gated", "401", "403", "unauthorized", "access to model")):
                raise RuntimeError(
                    f"\n[!] Model '{repository}' is a GATED model requiring license acceptance.\n\n"
                    "User Action Steps:\n"
                    f" 1. Open in browser: https://huggingface.co/{repository}\n"
                    " 2. Click 'Accept License / Request Access'\n"
                    " 3. Get your Access Token from: https://huggingface.co/settings/tokens\n"
                    " 4. Run: aq login <YOUR_TOKEN>\n"
                    f" 5. Re-run: aq pull {repository}\n"
                ) from error
            raise RuntimeError(f"Download failed: {str(error)}") from error
        return self.storage.model_name(repository)

    def start_background_pull(self, repository: str, token: str | None = None) -> dict:
        """Spawn daemon thread for non-blocking model download."""
        if ModelManager._download_state.get("status") == "downloading":
            return dict(ModelManager._download_state)

        from aqruntime.model.power_lock import PowerLockManager
        PowerLockManager.acquire_lock()

        ModelManager._download_state.update({
            "status": "downloading",
            "repository": repository,
            "model": self.storage.model_name(repository),
            "error": None,
            "sleep_lock_active": True,
        })

        def _worker():
            try:
                model_name = self.download(repository, token=token)
                ModelManager._download_state.update({
                    "status": "completed",
                    "model": model_name,
                    "sleep_lock_active": False,
                })
            except Exception as err:
                ModelManager._download_state.update({
                    "status": "failed",
                    "error": str(err),
                    "sleep_lock_active": False,
                })
            finally:
                PowerLockManager.release_lock()

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()
        return dict(ModelManager._download_state)

    def get_pull_status(self) -> dict:
        """Return current background download status."""
        from aqruntime.model.power_lock import PowerLockManager
        status = dict(ModelManager._download_state)
        status["sleep_lock_active"] = PowerLockManager.is_locked()
        return status

    def inspect_download_state(self, repository: str) -> dict:
        """Inspect if model is 100% installed or partially cached."""
        model_name = self.storage.model_name(repository)
        path = self.storage.path_for(repository)

        if path.is_dir():
            has_weights = GGUFModelLoader.is_gguf_dir(path) or any(
                f.name.endswith((".safetensors", ".bin", ".h5")) for f in path.glob("*")
            )
            if has_weights:
                return {
                    "is_installed": True,
                    "is_partial": False,
                    "model_name": model_name,
                    "percentage": 100.0,
                }

        from pathlib import Path
        cache_dir = Path.home() / ".cache" / "huggingface" / "hub" / f"models--{repository.replace('/', '--')}"
        if cache_dir.exists():
            cached_bytes = sum(f.stat().st_size for f in cache_dir.glob("**/*") if f.is_file())
            if cached_bytes > 10 * 1024 * 1024:
                gb = cached_bytes / (1024 ** 3)
                return {
                    "is_installed": False,
                    "is_partial": True,
                    "model_name": model_name,
                    "cached_bytes": cached_bytes,
                    "cached_gb": round(gb, 2),
                    "percentage": 70.0,
                }

        return {
            "is_installed": False,
            "is_partial": False,
            "model_name": model_name,
            "percentage": 0.0,
        }

    def reset_cache_and_pull(self, repository: str, token: str | None = None) -> dict:
        """Delete partial cache files and launch fresh background download."""
        from pathlib import Path
        import shutil

        dest = self.storage.path_for(repository)
        if dest.exists():
            try:
                shutil.rmtree(dest)
            except Exception:
                pass

        cache_dir = Path.home() / ".cache" / "huggingface" / "hub" / f"models--{repository.replace('/', '--')}"
        if cache_dir.exists():
            try:
                shutil.rmtree(cache_dir)
            except Exception:
                pass

        return self.start_background_pull(repository, token=token)

    def load(self, model: str):
        path = self.storage.path_for(model)
        if not path.is_dir():
            raise FileNotFoundError("Model not found.")

        # Dual Backend Routing: GGUF vs PyTorch Transformers
        if GGUFModelLoader.is_gguf_dir(path):
            return GGUFModelLoader.load_gguf(path)

        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            tokenizer = AutoTokenizer.from_pretrained(str(path), local_files_only=True)
            load_kwargs = {
                "local_files_only": True,
                "torch_dtype": "auto",
                "low_cpu_mem_usage": True,
            }
            language_model = AutoModelForCausalLM.from_pretrained(str(path), **load_kwargs)
            language_model.eval()
            return tokenizer, language_model
        except Exception as error:
            raise RuntimeError(f"Failed to load model weights: {str(error)}") from error

"""Local file-system storage for downloaded models."""

from pathlib import Path
import re
import shutil


class StorageManager:
    def __init__(self, model_directory: Path) -> None:
        self.model_directory = model_directory
        self.model_directory.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def model_name(model: str) -> str:
        name = re.sub(r"[^a-z0-9]+", "-", model.strip().lower()).strip("-")
        if not name:
            raise ValueError("Model name cannot be empty.")
        return name

    def path_for(self, model: str) -> Path:
        model_root = self.model_directory.resolve()
        clean_input = model.strip().lower()

        # Keep a raw repository path only when it stays inside the storage root.
        try:
            raw_path = (self.model_directory / clean_input).resolve()
            if raw_path.is_relative_to(model_root) and raw_path.is_dir():
                return raw_path
        except (OSError, ValueError):
            pass

        sanitized_name = self.model_name(model)
        sanitized_path = self.model_directory / sanitized_name
        if sanitized_path.is_dir():
            return sanitized_path

        if self.model_directory.exists():
            candidates = [
                entry for entry in self.model_directory.iterdir()
                if entry.is_dir() and (clean_input in entry.name or entry.name in clean_input)
            ]
            # Candidate paths come from iterdir(), so they are inherently contained.
            if len(candidates) == 1:
                return candidates[0].resolve()
        return sanitized_path

    @staticmethod
    def classify_model(model_name: str) -> str:
        name = str(model_name).lower()
        audio_markers = ("whisper", "audio", "speech", "stt", "tts", "sensevoice")
        vision_markers = ("vision", "moondream", "paligemma", "llava", "qwen-vl", "qwen2-vl", "smolvlm")
        if any(marker in name for marker in audio_markers):
            return "audio"
        if any(marker in name for marker in vision_markers):
            return "vision"
        return "text"

    @staticmethod
    def model_capabilities(model_name: str) -> dict:
        model_type = StorageManager.classify_model(model_name)
        return {
            "type": model_type,
            "chat": model_type == "text",
            "streaming": True,
            "tools": model_type == "text",
            "vision": False,
            "audio_transcription": False,
            "embedding": False,
        }

    def list_models(self) -> list[str]:
        if not self.model_directory.exists():
            return []
        return sorted(entry.name for entry in self.model_directory.iterdir() if entry.is_dir())

    def list_chat_models(self) -> list[str]:
        return [model for model in self.list_models() if self.classify_model(model) == "text"]

    def remove(self, model: str) -> bool:
        path = self.path_for(model)
        model_root = self.model_directory.resolve()
        try:
            resolved = path.resolve()
        except (OSError, ValueError):
            return False
        if not resolved.is_relative_to(model_root):
            return False
        if not resolved.is_dir():
            return False
        shutil.rmtree(resolved)
        return True

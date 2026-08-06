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
        clean_input = model.strip().lower()
        raw_path = self.model_directory / clean_input
        if raw_path.is_dir():
            return raw_path
        sanitized_name = self.model_name(model)
        sanitized_path = self.model_directory / sanitized_name
        if sanitized_path.is_dir():
            return sanitized_path
        if self.model_directory.exists():
            candidates = [
                entry for entry in self.model_directory.iterdir()
                if entry.is_dir() and (clean_input in entry.name or entry.name in clean_input)
            ]
            if len(candidates) == 1:
                return candidates[0]
        return sanitized_path

    def list_models(self) -> list[str]:
        if not self.model_directory.exists():
            return []
        return sorted(entry.name for entry in self.model_directory.iterdir() if entry.is_dir())

    def remove(self, model: str) -> bool:
        path = self.path_for(model)
        if not path.is_dir():
            return False
        shutil.rmtree(path)
        return True

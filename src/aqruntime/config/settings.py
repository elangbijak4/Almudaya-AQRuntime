"""Persistent runtime configuration."""

from dataclasses import dataclass
from pathlib import Path
import os
import yaml


@dataclass(frozen=True)
class RuntimeSettings:
    version: str
    default_model: str | None
    model_directory: Path
    log_directory: Path
    hf_token: str | None = None
    root_directory: Path | None = None


def project_root() -> Path:
    override = os.getenv("AQRUNTIME_HOME")
    return Path(override).expanduser().resolve() if override else Path.cwd()


def load_settings(root: Path | None = None) -> RuntimeSettings:
    root = root or project_root()
    config_path = root / "config" / "runtime.yaml"
    try:
        with config_path.open(encoding="utf-8") as stream:
            values = yaml.safe_load(stream) or {}
    except FileNotFoundError as error:
        raise RuntimeError(f"Configuration error: {config_path} was not found.") from error
    except yaml.YAMLError as error:
        raise RuntimeError("Configuration error: runtime.yaml is invalid.") from error
    try:
        version = str(values["runtime_version"])
        model_directory = root / str(values["model_directory"])
        log_directory = root / str(values["log_directory"])
        hf_token = values.get("hf_token") or os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN")
    except KeyError as error:
        raise RuntimeError(f"Configuration error: missing {error.args[0]}.") from error
    return RuntimeSettings(
        version,
        values.get("default_model"),
        model_directory,
        log_directory,
        hf_token,
        root,
    )


def save_token(token: str, root: Path | None = None) -> None:
    root = root or project_root()
    config_path = root / "config" / "runtime.yaml"
    data = {
        "runtime_version": "0.4.0",
        "default_model": None,
        "model_directory": "models",
        "log_directory": "logs",
    }
    if config_path.exists():
        try:
            with config_path.open("r", encoding="utf-8") as stream:
                existing = yaml.safe_load(stream) or {}
                data.update(existing)
        except Exception:
            pass
    data["hf_token"] = token.strip()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with config_path.open("w", encoding="utf-8") as stream:
        yaml.safe_dump(data, stream)


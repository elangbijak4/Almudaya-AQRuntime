"""Abstract Base Class for AQRuntime Execution Providers."""

from abc import ABC, abstractmethod
from pathlib import Path


class ExecutionProvider(ABC):
    """Abstract Base Class for hardware execution engines."""

    name: str = "base"
    display_name: str = "Base Provider"
    priority: int = 99

    @abstractmethod
    def is_available(self) -> tuple[bool, str]:
        """Check if hardware/driver/library is available on the system."""
        pass

    @abstractmethod
    def get_info(self) -> dict:
        """Return detailed status, driver info, and task capabilities."""
        pass

    @abstractmethod
    def can_run_model(self, model_path: Path) -> bool:
        """Check if provider supports executing the given model architecture/file."""
        pass

    @abstractmethod
    def load_model(self, model_path: Path):
        """Load tokenizer and model on this execution provider."""
        pass

    @abstractmethod
    def generate(self, model_instance, formatted_prompt: str) -> str:
        """Generate completion response using this provider."""
        pass

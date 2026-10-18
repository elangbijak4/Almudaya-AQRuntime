"""Conversation Memory Manager for Short-Term and Long-Term Memory."""

import re
from datetime import datetime
import json
from pathlib import Path


class MemoryManager:
    """Manage Short-Term Memory (sliding window context) and Long-Term Memory (JSON persistence)."""

    def __init__(self, root_dir: Path) -> None:
        self.memory_dir = root_dir / "memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)

    def _session_file(self, session_name: str) -> Path:
        # Allow only filesystem-safe session names and prevent traversal.
        safe_name = re.sub(r"[^a-z0-9._-]", "-", str(session_name).strip().lower())
        safe_name = safe_name.strip(".-") or "session"
        path = (self.memory_dir / f"{safe_name}.json").resolve()
        if not path.is_relative_to(self.memory_dir.resolve()):
            raise ValueError("Invalid session name.")
        return path

    def load_session(self, session_name: str) -> list[dict]:
        file_path = self._session_file(session_name)
        if not file_path.exists():
            return []
        try:
            with file_path.open("r", encoding="utf-8") as stream:
                data = json.load(stream)
                return data.get("messages", [])
        except Exception:
            return []

    def save_session(self, session_name: str, messages: list[dict]) -> None:
        file_path = self._session_file(session_name)
        persistent_turns = [m for m in messages if m.get("role") in ("user", "assistant")]
        data = {
            "session_name": session_name,
            "updated_at": datetime.now().isoformat(),
            "messages": persistent_turns,
        }
        with file_path.open("w", encoding="utf-8") as stream:
            json.dump(data, stream, indent=2)

    def list_sessions(self) -> list[dict]:
        results = []
        for file_path in sorted(self.memory_dir.glob("*.json")):
            try:
                with file_path.open("r", encoding="utf-8") as stream:
                    data = json.load(stream)
                    turns = len(data.get("messages", []))
                    results.append(
                        {
                            "name": file_path.stem,
                            "updated_at": data.get("updated_at", "Unknown"),
                            "turns": turns,
                        }
                    )
            except Exception:
                pass
        return results

    def clear_session(self, session_name: str) -> bool:
        file_path = self._session_file(session_name)
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def copy_session(self, source_session: str, target_session: str) -> bool:
        messages = self.load_session(source_session)
        if not messages:
            return False
        self.save_session(target_session, messages)
        return True

    def get_session_messages(self, session_name: str) -> list[dict]:
        return self.load_session(session_name)

    def export_session(self, session_name: str, target_file: Path) -> bool:
        messages = self.load_session(session_name)
        if not messages:
            return False
        lines = [f"# Memory Session Export: {session_name}\n"]
        for m in messages:
            role = m.get("role", "user").capitalize()
            content = m.get("content", "")
            lines.append(f"### {role}\n{content}\n")
        target_file.parent.mkdir(parents=True, exist_ok=True)
        with target_file.open("w", encoding="utf-8") as stream:
            stream.write("\n".join(lines))
        return True

    @staticmethod
    def apply_short_term_window(messages: list[dict], max_history_turns: int = 10) -> list[dict]:
        """Keep system prompt at index 0 and sliding window of recent user/assistant turns."""
        system_prompts = [m for m in messages if m.get("role") == "system"]
        chat_turns = [m for m in messages if m.get("role") in ("user", "assistant")]
        recent_turns = chat_turns[-max_history_turns:]
        return system_prompts + recent_turns

"""Cross-platform OS Sleep Prevention & Power Lock Manager."""

import ctypes
import sys


class PowerLockManager:
    """Prevents system sleep/hibernate during active background downloads."""

    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001
    ES_DISPLAY_REQUIRED = 0x00000002

    _locked: bool = False

    @classmethod
    def acquire_lock(cls) -> bool:
        """Prevent host OS sleep timer."""
        if sys.platform == "win32":
            try:
                flags = cls.ES_CONTINUOUS | cls.ES_SYSTEM_REQUIRED
                ctypes.windll.kernel32.SetThreadExecutionState(flags)
                cls._locked = True
                return True
            except Exception:
                pass
        cls._locked = True
        return True

    @classmethod
    def release_lock(cls) -> bool:
        """Restore default host OS sleep timer."""
        if sys.platform == "win32":
            try:
                ctypes.windll.kernel32.SetThreadExecutionState(cls.ES_CONTINUOUS)
                cls._locked = False
                return True
            except Exception:
                pass
        cls._locked = False
        return True

    @classmethod
    def is_locked(cls) -> bool:
        return cls._locked

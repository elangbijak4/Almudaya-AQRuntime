"""System hardware inspection and capacity calculator."""

import ctypes
import os
import platform
import sys


class HardwareDetector:
    """Detect system RAM and compute safe model parameter capacity limits."""

    def __init__(self) -> None:
        self.processor_name = platform.processor() or "Generic Processor"
        self.cpu_cores = os.cpu_count() or 1
        total_bytes, avail_bytes = self._get_ram_info()
        self.total_ram_gb = round(total_bytes / (1024 ** 3), 2)
        self.available_ram_gb = round(avail_bytes / (1024 ** 3), 2)

    def _get_ram_info(self) -> tuple[int, int]:
        """Return (total_bytes, available_bytes)."""
        if sys.platform == "win32":
            try:
                class MEMORYSTATUSEX(ctypes.Structure):
                    _fields_ = [
                        ("dwLength", ctypes.c_ulong),
                        ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong),
                        ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong),
                        ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong),
                        ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
                    ]

                stat = MEMORYSTATUSEX()
                stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
                if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)):
                    return int(stat.ullTotalPhys), int(stat.ullAvailPhys)
            except Exception:
                pass
        elif sys.platform == "linux":
            try:
                mem_total = 0
                mem_avail = 0
                with open("/proc/meminfo", "r", encoding="utf-8") as stream:
                    for line in stream:
                        parts = line.split(":")
                        if len(parts) == 2:
                            key = parts[0].strip()
                            val = int(parts[1].split()[0]) * 1024
                            if key == "MemTotal":
                                mem_total = val
                            elif key in ("MemAvailable", "MemFree"):
                                if not mem_avail or key == "MemAvailable":
                                    mem_avail = val
                if mem_total:
                    return mem_total, mem_avail or mem_total // 2
            except Exception:
                pass
        # Fallback default: 16 GB total, 8 GB available
        return 16 * 1024 * 1024 * 1024, 8 * 1024 * 1024 * 1024

    def max_safe_param_size(self) -> float:
        """Calculate max safe model parameter size in billions for FP16 inference."""
        safe_ram = max(1.0, self.total_ram_gb - 4.0)
        return round(safe_ram / 2.2, 1)

    def max_safe_param_size_gguf(self) -> float:
        """Calculate max safe model parameter size in billions for GGUF 4-bit quantized inference."""
        safe_ram = max(1.0, self.total_ram_gb - 2.0)
        return round(safe_ram / 0.7, 1)

    def is_model_compatible(self, param_size_b: float, is_gguf: bool = False) -> str:
        """Classify model compatibility based on hardware specs."""
        max_safe = self.max_safe_param_size_gguf() if is_gguf else self.max_safe_param_size()
        if param_size_b <= max_safe:
            return "COMPATIBLE"
        if param_size_b <= max_safe * 1.4:
            return "HIGH_RAM"
        return "INCOMPATIBLE"

    def get_summary(self) -> dict:
        return {
            "os": platform.system() + " " + platform.release(),
            "cpu": self.processor_name,
            "cpu_cores": self.cpu_cores,
            "total_ram_gb": self.total_ram_gb,
            "available_ram_gb": self.available_ram_gb,
            "max_safe_param_b": self.max_safe_param_size(),
            "max_safe_gguf_param_b": self.max_safe_param_size_gguf(),
        }

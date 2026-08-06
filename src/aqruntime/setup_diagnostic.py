"""Pre-installation and hardware capability diagnostic tool for AQRuntime."""

from aqruntime.hardware import HardwareDetector

MINIMUM_RAM_GB = 4.0
LIGHTEST_RECOMMENDED_MODEL = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
LIGHTEST_MODEL_EST_RAM_GB = 2.5


def run_preinstall_check() -> dict:
    """Check host hardware capabilities against minimum software requirements."""
    detector = HardwareDetector()
    summary = detector.get_summary()
    total_ram = summary["total_ram_gb"]
    avail_ram = summary["available_ram_gb"]
    cores = summary.get("cpu_cores", 1)
    os_name = summary.get("os", "Unknown OS")

    is_capable = total_ram >= MINIMUM_RAM_GB
    status = "PASS" if is_capable else "FAIL_BELOW_MINIMUM"

    recommendation = {
        "status": status,
        "is_capable": is_capable,
        "hardware": {
            "os": os_name,
            "total_ram_gb": total_ram,
            "available_ram_gb": avail_ram,
            "cpu_cores": cores,
        },
        "minimum_requirement": {
            "min_ram_gb": MINIMUM_RAM_GB,
            "lightest_model": LIGHTEST_RECOMMENDED_MODEL,
            "lightest_model_ram_gb": LIGHTEST_MODEL_EST_RAM_GB,
        },
    }
    return recommendation


def main() -> None:
    result = run_preinstall_check()
    hw = result["hardware"]
    req = result["minimum_requirement"]
    print("==================================================================")
    print("             AQRuntime Setup Hardware Diagnostic                  ")
    print("==================================================================")
    print(f"OS          : {hw['os']}")
    print(f"Total RAM   : {hw['total_ram_gb']:.2f} GB (Available: {hw['available_ram_gb']:.2f} GB)")
    print(f"CPU Cores   : {hw['cpu_cores']}")
    print("------------------------------------------------------------------")
    if result["is_capable"]:
        print("Status      : [PASS] System meets minimum hardware requirements.")
        print(f"Entry Model : Recommended lightest entry model is '{req['lightest_model']}' (~{req['lightest_model_ram_gb']} GB RAM).")
    else:
        print("Status      : [WARNING / FAIL] System is below minimum requirements!")
        print(f"Requirement : Minimum {req['min_ram_gb']} GB RAM is required for entry models.")
        print(f"Lightest Model '{req['lightest_model']}' requires ~{req['lightest_model_ram_gb']} GB RAM.")
        print("Installation or execution may experience severe slowdowns or memory exhaustion.")
    print("==================================================================")


if __name__ == "__main__":
    main()

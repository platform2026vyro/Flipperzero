#!/usr/bin/env python3
"""Utilities for Flipper-Z Android"""

import os
import sys
import platform
import subprocess
from typing import List, Tuple


def clear_screen():
    os.system("clear" if os.name == "posix" else "cls")


def get_device_info() -> List[Tuple[str, str, str]]:
    info = []

    # NFC
    nfc_available = os.path.exists("/system/bin/nfc") or os.path.exists("/dev/nfc")
    nfc_status = "Available" if nfc_available else "Limited"
    nfc_detail = "Hardware NFC detected" if nfc_available else "Use termux-nfc or external reader"
    info.append(("NFC", nfc_status, nfc_detail))

    # Bluetooth
    try:
        result = subprocess.run(
            ["termux-bluetooth-scan", "--help"],
            capture_output=True, text=True, timeout=3
        )
        bt_status = "Available"
        bt_detail = "BLE via termux-api"
    except:
        bt_status = "Limited"
        bt_detail = "Install termux-api, try: pkg install termux-api"
    info.append(("Bluetooth/BLE", bt_status, bt_detail))

    # WiFi
    wifi_available = os.path.exists("/system/bin/iw") or os.path.exists("/system/bin/wpa_cli")
    wifi_status = "Available" if wifi_available else "Limited"
    wifi_detail = "WiFi chip detected" if wifi_available else "Root may be needed for monitor mode"
    info.append(("WiFi", wifi_status, wifi_detail))

    # IR Blaster
    ir_paths = ["/dev/ir", "/sys/class/ir", "/dev/ir_rx", "/com.android.server.telecom"]
    ir_available = any(os.path.exists(p) for p in ir_paths)
    ir_status = "Available" if ir_available else "Unavailable"
    ir_detail = "IR hardware detected" if ir_available else "Most phones lack IR blaster"
    info.append(("Infrared", ir_status, ir_detail))

    # Root
    root_available = os.geteuid() == 0 if hasattr(os, "geteuid") else False
    if not root_available:
        try:
            result = subprocess.run(["su", "-c", "echo 1"], capture_output=True, text=True, timeout=2)
            root_available = result.stdout.strip() == "1"
        except:
            pass
    root_status = "Available" if root_available else "Unavailable"
    root_detail = "Full system access" if root_available else "Most features work without root"
    info.append(("Root Access", root_status, root_detail))

    # Termux-API
    try:
        subprocess.run(["termux-wifi-scaninfo", "--help"], capture_output=True, timeout=2)
        api_status = "Available"
        api_detail = "All termux-api features ready"
    except:
        api_status = "Missing"
        api_detail = "Run: pkg install termux-api"
    info.append(("Termux-API", api_status, api_detail))

    # Python packages
    packages = {}
    for pkg in ["bleak", "nfcpy", "scapy"]:
        try:
            __import__(pkg.replace("-", "_"))
            packages[pkg] = "Installed"
        except ImportError:
            packages[pkg] = "Not installed"
    pkg_status = "All" if all(v == "Installed" for v in packages.values()) else "Partial"
    pkg_detail = ", ".join(f"{k}: {v}" for k, v in packages.items())
    info.append(("Python Packages", pkg_status, pkg_detail))

    return info


def check_dependencies() -> List[str]:
    missing = []
    try:
        import rich
    except ImportError:
        missing.append("rich")
    return missing


def run_termux_command(cmd: list) -> dict:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return {"success": result.returncode == 0, "output": result.stdout, "error": result.stderr}
    except subprocess.TimeoutExpired:
        return {"success": False, "output": "", "error": "Timeout"}
    except FileNotFoundError:
        return {"success": False, "output": "", "error": "Command not found"}
    except Exception as e:
        return {"success": False, "output": "", "error": str(e)}


def hex_to_bytes(hex_str: str) -> bytes:
    return bytes.fromhex(hex_str.replace(" ", ""))


def bytes_to_hex(b: bytes, sep: str = " ") -> str:
    return sep.join(f"{x:02x}" for x in b)

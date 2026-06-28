#!/usr/bin/env python3
"""
FLIPPER-Z ANDROID - Main Entry Point
Flipper Zero-like tool suite for Android Termux
"""

import sys
import os

NON_INTERACTIVE = len(sys.argv) > 1

if NON_INTERACTIVE:
    import rich.prompt
    def _mock_ask(prompt="", default="", *a, **kw): return default
    def _mock_confirm(prompt="", default=True, *a, **kw): return default
    rich.prompt.Prompt.ask = _mock_ask
    rich.prompt.Confirm.ask = _mock_confirm

from rich.console import Console
from rich.table import Table
from rich import box
from rich.prompt import Prompt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.utils import clear_screen
from modules.nfc_tools import NfcTools
from modules.ble_tools import BleScanner
from modules.wifi_scan import WifiScan
from modules.bruteforce import BruteForce
from modules.scooter_unlock import ScooterUnlock
from modules.ir_remote import IrRemote
from modules.network_remote import NetworkRemote
from modules.system_tools import SystemTools
from modules.device_info import DeviceInfo

console = Console()

APP_NAME = "[bold cyan]FLIPPER-Z[/bold cyan] [white]ANDROID[/white]"
VERSION = "2.0.0"

MENU_ITEMS = [
    {"icon": "📡", "name": "NFC Tools",       "desc": "Read NFC tags (via termux-nfc)",                "color": "blue"},
    {"icon": "🔵", "name": "BLE Scanner",     "desc": "Scan BLE devices (via termux-bluetooth-scan)",  "color": "cyan"},
    {"icon": "📶", "name": "WiFi Scan",       "desc": "Scan WiFi & ping sweep",                        "color": "green"},
    {"icon": "⚡",  "name": "Brute Force",    "desc": "Hash, ZIP, PDF cracker, wordlist, PIN, rainbow","color": "red"},
    {"icon": "🛴", "name": "Scooter Unlock",  "desc": "BLE scooter unlock (Xiaomi/Ninebot)",           "color": "yellow"},
    {"icon": "📺", "name": "IR Remote",       "desc": "TV remote codes (Samsung, LG, Sony, Xiaomi)",   "color": "yellow"},
    {"icon": "🌐", "name": "Network Remote",  "desc": "Control TVs via WiFi (HTTP API)",               "color": "cyan"},
    {"icon": "🛠️", "name": "System Tools",   "desc": "Nmap, Hydra, SQLMap, GoBuster, FFUF, John...",  "color": "magenta"},
    {"icon": "📱", "name": "Device Info",     "desc": "Battery, sensors, telephony info",              "color": "green"},
    {"icon": "🚪", "name": "Exit",            "desc": "Exit Flipper-Z",                                "color": "red"},
]


def show_banner():
    banner_path = os.path.join(os.path.dirname(__file__), "assets", "flipper_ascii.txt")
    if os.path.exists(banner_path):
        with open(banner_path) as f:
            banner = f.read()
        console.print(f"[cyan]{banner}[/cyan]")
    else:
        console.print(f"[bold cyan]FLIPPER-Z ANDROID v{VERSION}[/bold cyan]")
    console.print(f"[bold white]┃  Hacking Suite — Only Real Tools  ┃[/bold white]")
    console.print(f"[bold white]┃       v{VERSION}                        ┃[/bold white]")
    console.print("━" * 40, style="cyan")


def show_menu():
    clear_screen()
    show_banner()

    table = Table(box=box.ROUNDED, border_style="cyan", show_header=False, padding=(1, 2))
    table.add_column("Option", style="bold yellow", width=4)
    table.add_column("Tool", width=22)
    table.add_column("Description", style="white", width=42)

    for i, item in enumerate(MENU_ITEMS, 1):
        color = item["color"]
        name = f"[{color}]{item['icon']} {item['name']}[/{color}]"
        table.add_row(f"[bold]{i}[/bold]", name, item["desc"])

    console.print(table)
    console.print()


def main():
    try:
        first = True
        while True:
            if first and len(sys.argv) > 1 and sys.argv[1].lstrip("-").isdigit():
                choice = int(sys.argv[1])
                first = False
            else:
                show_menu()
                try:
                    choice = Prompt.ask("[bold yellow]Select option[/bold yellow]", default="10")
                    choice = int(choice)
                except (ValueError, TypeError):
                    console.print("[red]Invalid selection. Enter a number.[/red]")
                    continue

            if choice < 1 or choice > len(MENU_ITEMS):
                console.print("[red]Invalid selection. Try again.[/red]")
                continue

            if choice == len(MENU_ITEMS):
                clear_screen()
                console.print("[bold cyan]Goodbye! 🐬[/bold cyan]")
                sys.exit(0)

            handlers = {
                1: lambda: NfcTools(console).menu(),
                2: lambda: BleScanner(console).menu(),
                3: lambda: WifiScan(console).menu(),
                4: lambda: BruteForce(console).menu(),
                5: lambda: ScooterUnlock(console).menu(),
                6: lambda: IrRemote(console).menu(),
                7: lambda: NetworkRemote(console).menu(),
                8: lambda: SystemTools(console).menu(),
                9: lambda: DeviceInfo(console).menu(),
            }

            handlers[choice]()

            if NON_INTERACTIVE:
                break
    except KeyboardInterrupt:
        clear_screen()
        console.print("[bold cyan]Goodbye! 🐬[/bold cyan]")
        sys.exit(0)


if __name__ == "__main__":
    main()

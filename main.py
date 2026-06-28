#!/usr/bin/env python3
"""
FLIPPER-Z ANDROID - Main Entry Point
Flipper Zero-like tool suite for Android Termux
"""

import sys
import os
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.prompt import Prompt
from rich.text import Text

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.utils import clear_screen, check_dependencies, get_device_info
from modules.nfc_tools import NfcTools
from modules.ble_tools import BleTools
from modules.wifi_tools import WifiTools
from modules.bruteforce import BruteForce
from modules.subghz_tools import SubGhzTools
from modules.badusb_tools import BadUsbTools
from modules.ir_remote import IrRemote
from modules.network_remote import NetworkRemote
from modules.system_tools import SystemTools

console = Console()

APP_NAME = "[bold cyan]FLIPPER-Z[/bold cyan] [white]ANDROID[/white]"
VERSION = "1.1.0"

MENU_ITEMS = [
    {"icon": "📡", "name": "NFC Tools", "desc": "Read, write, clone NFC tags & badges", "color": "cyan"},
    {"icon": "🔵", "name": "BLE Scanner", "desc": "Bluetooth Low Energy scan & attacks", "color": "blue"},
    {"icon": "📶", "name": "WiFi Tools", "desc": "Scan, deauth, capture handshake", "color": "green"},
    {"icon": "⚡", "name": "Brute Force", "desc": "PIN, password, UID brute forcing", "color": "red"},
    {"icon": "📻", "name": "Sub-GHz", "desc": "RF signal simulation (experimental)", "color": "yellow"},
    {"icon": "⌨️", "name": "BadUSB", "desc": "HID attack scripts for OTG", "color": "magenta"},
    {"icon": "📺", "name": "IR Remote", "desc": "TV IR codes (needs IR blaster)", "color": "yellow"},
    {"icon": "🌐", "name": "Network Remote", "desc": "Smart TV via WiFi (no IR)", "color": "cyan"},
    {"icon": "🛠️", "name": "System Tools", "desc": "Hydra, John, Nmap, SQLMap, GoBuster...", "color": "magenta"},
    {"icon": "ℹ️", "name": "Device Info", "desc": "Show phone hardware capabilities", "color": "white"},
    {"icon": "🚪", "name": "Exit", "desc": "Exit Flipper-Z", "color": "red"},
]


def show_banner():
    banner_path = os.path.join(os.path.dirname(__file__), "assets", "flipper_ascii.txt")
    if os.path.exists(banner_path):
        with open(banner_path) as f:
            banner = f.read()
        console.print(f"[cyan]{banner}[/cyan]")
    else:
        console.print(f"[bold cyan]FLIPPER-Z ANDROID v{VERSION}[/bold cyan]")
    console.print(f"[bold white]┃  Flipper Zero Clone for Termux  ┃[/bold white]")
    console.print(f"[bold white]┃       v{VERSION}                        ┃[/bold white]")
    console.print("━" * 40, style="cyan")


def show_menu():
    clear_screen()
    show_banner()

    table = Table(box=box.ROUNDED, border_style="cyan", show_header=False, padding=(1, 2))
    table.add_column("Option", style="bold yellow", width=4)
    table.add_column("Tool", width=20)
    table.add_column("Description", style="white", width=40)

    for i, item in enumerate(MENU_ITEMS, 1):
        color = item["color"]
        name = f"[{color}]{item['icon']} {item['name']}[/{color}]"
        table.add_row(f"[bold]{i}[/bold]", name, item["desc"])

    console.print(table)
    console.print()


def handle_nfc():
    nfc = NfcTools(console)
    nfc.menu()


def handle_ble():
    ble = BleTools(console)
    ble.menu()


def handle_wifi():
    wifi = WifiTools(console)
    wifi.menu()


def handle_bruteforce():
    bf = BruteForce(console)
    bf.menu()


def handle_subghz():
    sg = SubGhzTools(console)
    sg.menu()


def handle_badusb():
    bu = BadUsbTools(console)
    bu.menu()


def handle_ir():
    ir = IrRemote(console)
    ir.menu()


def handle_network_remote():
    nr = NetworkRemote(console)
    nr.menu()


def handle_system_tools():
    st = SystemTools(console)
    st.menu()


def handle_device_info():
    clear_screen()
    show_banner()
    info = get_device_info()
    table = Table(title="[bold cyan]Device Hardware Info[/bold cyan]", box=box.ROUNDED, border_style="cyan")
    table.add_column("Feature", style="bold yellow")
    table.add_column("Status", style="bold")
    table.add_column("Details", style="white")

    for feat, status, details in info:
        status_style = "green" if status == "Available" else "red" if status == "Unavailable" else "yellow"
        table.add_row(feat, f"[{status_style}]{status}[/{status_style}]", details)

    console.print(table)
    console.print("\n[dim]Note: Some features require root or specific hardware[/dim]")
    Prompt.ask("[bold yellow]Press Enter to return[/bold yellow]")


def main():
    try:
        while True:
            show_menu()
            try:
                choice = Prompt.ask("[bold yellow]Select option[/bold yellow]", default="11")
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
                1: handle_nfc,
                2: handle_ble,
                3: handle_wifi,
                4: handle_bruteforce,
                5: handle_subghz,
                6: handle_badusb,
                7: handle_ir,
                8: handle_network_remote,
                9: handle_system_tools,
                10: handle_device_info,
            }

            handlers[choice]()
    except KeyboardInterrupt:
        clear_screen()
        console.print("[bold cyan]Goodbye! 🐬[/bold cyan]")
        sys.exit(0)


if __name__ == "__main__":
    main()

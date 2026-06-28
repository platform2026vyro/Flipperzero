#!/usr/bin/env python3
"""
FLIPPER-Z ANDROID - Main Entry Point
Flipper Zero-like tool suite for Android Termux
"""

import sys
import os

# auto non-interactive when any arg is passed
NON_INTERACTIVE = len(sys.argv) > 1

if NON_INTERACTIVE:
    import rich.prompt

    def _mock_ask(prompt="", default="", *a, **kw):
        return default

    def _mock_confirm(prompt="", default=True, *a, **kw):
        return default

    rich.prompt.Prompt.ask = _mock_ask
    rich.prompt.Confirm.ask = _mock_confirm

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.prompt import Prompt
from rich.text import Text

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.utils import clear_screen, check_dependencies, get_device_info
from modules.bruteforce import BruteForce
from modules.ir_remote import IrRemote
from modules.network_remote import NetworkRemote
from modules.system_tools import SystemTools

console = Console()

APP_NAME = "[bold cyan]FLIPPER-Z[/bold cyan] [white]ANDROID[/white]"
VERSION = "2.0.0"

MENU_ITEMS = [
    {"icon": "⚡", "name": "Brute Force", "desc": "Hash, ZIP, PDF, wordlist, PIN analyzer — real tools", "color": "red"},
    {"icon": "📺", "name": "IR Remote", "desc": "TV IR codes (Samsung, LG, Sony, Panasonic, Xiaomi, TCL)", "color": "yellow"},
    {"icon": "🌐", "name": "Network Remote", "desc": "Control Smart TV via WiFi (real HTTP)", "color": "cyan"},
    {"icon": "🛠️", "name": "System Tools", "desc": "Nmap, Hydra, John, SQLMap, GoBuster, FFUF...", "color": "magenta"},
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
    console.print(f"[bold white]┃  Hacking Suite — Only Real Tools  ┃[/bold white]")
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


def handle_bruteforce():
    bf = BruteForce(console)
    bf.menu()


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
        first = True
        while True:
            if first and len(sys.argv) > 1 and sys.argv[1].lstrip("-").isdigit():
                choice = int(sys.argv[1])
                first = False
            else:
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
                1: handle_bruteforce,
                2: handle_ir,
                3: handle_network_remote,
                4: handle_system_tools,
                5: handle_device_info,
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

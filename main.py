#!/usr/bin/env python3
"""Android Utility Toolkit for Termux."""

import os
import sys
from rich.console import Console
from rich.table import Table
from rich import box
from rich.prompt import Prompt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Force UTF-8 for Windows console
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    # Add common tool paths
    tool_paths = [
        r"C:\Program Files (x86)\Nmap",
        r"C:\Program Files\Nmap",
        r"C:\Program Files (x86)\GnuWin32\bin",
        r"C:\Program Files\Git\usr\bin",
    ]
    for p in tool_paths:
        if os.path.isdir(p) and p not in os.environ.get("PATH", ""):
            os.environ["PATH"] = p + os.pathsep + os.environ.get("PATH", "")

from modules.utils import clear_screen
from modules.nfc_tools import NfcTools
from modules.ble_tools import BleScanner
from modules.wifi_scan import WifiScan
from modules.network_remote import NetworkRemote
from modules.system_tools import SystemTools
from modules.device_info import DeviceInfo
from modules.bruteforce import BruteForce
from modules.ir_remote import IrRemote
from modules.scooter_unlock import ScooterUnlock

console = Console()
VERSION = "3.1-safe"

MENU_ITEMS = [
    {"icon": ">", "name": "NFC Tools", "desc": "Lettura NFC tramite Termux:API", "color": "blue"},
    {"icon": ">", "name": "BLE Scanner", "desc": "Scansione BLE passiva", "color": "cyan"},
    {"icon": ">", "name": "WiFi Scan", "desc": "Info WiFi e reti visibili", "color": "green"},
    {"icon": ">", "name": "Network Remote", "desc": "Controlli HTTP autorizzati su dispositivi propri", "color": "cyan"},
    {"icon": ">", "name": "System Tools", "desc": "Ping, DNS, Whois, Nmap su target autorizzati", "color": "magenta"},
    {"icon": ">", "name": "Device Info", "desc": "Batteria, WiFi, device info", "color": "green"},
    {"icon": ">", "name": "Brute Force", "desc": "Crack hash, ZIP, PDF, wordlist, PIN generator", "color": "red"},
    {"icon": ">", "name": "IR Remote", "desc": "Codici infrarossi per TV (Samsung, LG, Sony...)", "color": "yellow"},
    {"icon": ">", "name": "Scooter Unlock", "desc": "Sblocco BLE Xiaomi/Ninebot via bleak/blesh", "color": "yellow"},
    {"icon": ">", "name": "Exit", "desc": "Chiudi", "color": "red"},
]


def show_banner():
    console.print(f"[bold cyan]FLIPPER-Z ANDROID SAFE v{VERSION}[/bold cyan]")
    console.print("[white]Toolkit Termux per diagnostica e gestione autorizzata[/white]")
    console.print("═" * 56, style="cyan")


def show_menu():
    clear_screen()
    show_banner()
    table = Table(box=box.ROUNDED, border_style="cyan", show_header=False, padding=(1, 2))
    table.add_column("N", style="bold yellow", width=4)
    table.add_column("Modulo", width=22)
    table.add_column("Descrizione", style="white", width=52)

    for i, item in enumerate(MENU_ITEMS, 1):
        table.add_row(f"[bold]{i}[/bold]", f"[{item['color']}]{item['icon']} {item['name']}[/{item['color']}]", item["desc"])
    console.print(table)


def main():
    handlers = {
        1: lambda: NfcTools(console).menu(),
        2: lambda: BleScanner(console).menu(),
        3: lambda: WifiScan(console).menu(),
        4: lambda: NetworkRemote(console).menu(),
        5: lambda: SystemTools(console).menu(),
        6: lambda: DeviceInfo(console).menu(),
        7: lambda: BruteForce(console).menu(),
        8: lambda: IrRemote(console).menu(),
        9: lambda: ScooterUnlock(console).menu(),
    }

    try:
        while True:
            show_menu()
            choice = Prompt.ask("[bold yellow]Scelta[/bold yellow]", default=str(len(MENU_ITEMS)))
            try:
                choice_num = int(choice)
            except ValueError:
                console.print("[red]Inserisci un numero valido.[/red]")
                continue

            if choice_num == len(MENU_ITEMS):
                clear_screen()
                console.print("[bold cyan]Chiuso.[/bold cyan]")
                return

            handler = handlers.get(choice_num)
            if handler is None:
                console.print("[red]Scelta non valida.[/red]")
                continue
            handler()
            Prompt.ask("[dim]Premi Invio per tornare al menu[/dim]", default="")
    except KeyboardInterrupt:
        clear_screen()
        console.print("[bold cyan]Chiuso.[/bold cyan]")


if __name__ == "__main__":
    main()

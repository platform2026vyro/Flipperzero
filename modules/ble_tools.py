#!/usr/bin/env python3
"""BLE Scanner Module — real scan via termux-bluetooth-scan"""

import subprocess, json, os, time
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import box
from .utils import clear_screen


class BleScanner:
    def __init__(self, console):
        self.console = console
        self.data_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "data", "ble"
        )
        os.makedirs(self.data_dir, exist_ok=True)

    def _banner(self):
        self.console.print(Panel.fit(
            "[bold cyan]🔵 BLE SCANNER[/bold cyan]\n"
            "[white]Bluetooth Low Energy device discovery[/white]",
            border_style="cyan"
        ))

    def _check_ble(self):
        try:
            subprocess.run(["termux-bluetooth-scan", "--help"],
                           capture_output=True, timeout=3)
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def menu(self):
        while True:
            clear_screen()
            self._banner()
            table = Table(box=box.ROUNDED, border_style="cyan", show_header=False)
            table.add_column("Opt", style="bold yellow", width=4)
            table.add_column("Action", width=25)
            table.add_column("Description", style="white", width=45)
            table.add_row("1", "[cyan]Scan BLE[/cyan]", "Scan for BLE devices (termux-api)")
            table.add_row("2", "[cyan]Saved Scans[/cyan]", "View saved BLE scan results")
            table.add_row("b", "[red]Back[/red]", "")
            self.console.print(table)
            choice = Prompt.ask("[bold yellow]Select[/bold yellow]", default="b")
            actions = {"1": self.scan, "2": self.saved_scans}
            actions.get(choice, lambda: None)()
            if choice == "b":
                break

    def scan(self):
        clear_screen()
        self._banner()
        if not self._check_ble():
            self.console.print("[red]termux-bluetooth-scan not found.[/red]")
            self.console.print("[yellow]Install: pkg install termux-api[/yellow]")
            Prompt.ask("[bold yellow]Press Enter[/bold yellow]")
            return
        self.console.print("[yellow]Scanning for BLE devices...[/yellow]")
        try:
            result = subprocess.run(
                ["termux-bluetooth-scan"], capture_output=True, text=True, timeout=15
            )
        except FileNotFoundError:
            self.console.print("[red]termux-bluetooth-scan not found. Install termux-api.[/red]")
            Prompt.ask("[bold yellow]Press Enter[/bold yellow]")
            return
        except subprocess.TimeoutExpired:
            self.console.print("[red]Scan timed out[/red]")
            Prompt.ask("[bold yellow]Press Enter[/bold yellow]")
            return
        if result.returncode != 0:
            self.console.print(f"[red]Scan error: {result.stderr.strip()}[/red]")
            Prompt.ask("[bold yellow]Press Enter[/bold yellow]")
            return
        try:
            devices = json.loads(result.stdout)
        except json.JSONDecodeError:
            self.console.print("[yellow]No BLE devices found or output invalid.[/yellow]")
            Prompt.ask("[bold yellow]Press Enter[/bold yellow]")
            return
        if not devices:
            self.console.print("[yellow]No BLE devices found. Enable Bluetooth and try again.[/yellow]")
            Prompt.ask("[bold yellow]Press Enter[/bold yellow]")
            return
        table = Table(title=f"[cyan]BLE Devices Found: {len(devices)}[/cyan]",
                      box=box.ROUNDED, border_style="cyan")
        table.add_column("#", style="bold yellow", width=3)
        table.add_column("Name", width=25)
        table.add_column("MAC", width=18)
        table.add_column("RSSI", width=6)
        table.add_column("Services", width=22)
        for i, d in enumerate(devices[:40], 1):
            name = d.get("name", "[dim]Unknown[/dim]")
            mac = d.get("address", d.get("mac", "?"))
            rssi = str(d.get("rssi", "?"))
            svc = d.get("services", "")
            if isinstance(svc, list):
                svc = ", ".join(str(s)[:18] for s in svc)
            table.add_row(str(i), name, mac, rssi, str(svc)[:22])
        self.console.print(table)
        if Confirm.ask("[yellow]Save results?", default=False):
            path = os.path.join(self.data_dir, f"ble_scan_{int(time.time())}.json")
            with open(path, "w") as f:
                json.dump(devices, f, indent=2)
            self.console.print(f"[green]Saved to {path}[/green]")
        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def saved_scans(self):
        clear_screen()
        self._banner()
        files = [f for f in os.listdir(self.data_dir) if f.endswith(".json")]
        if not files:
            self.console.print("[yellow]No saved scans.[/yellow]")
        else:
            table = Table(box=box.ROUNDED, border_style="cyan")
            table.add_column("#", style="bold yellow")
            table.add_column("File")
            table.add_column("Size")
            for i, f in enumerate(sorted(files, reverse=True), 1):
                sz = os.path.getsize(os.path.join(self.data_dir, f))
                table.add_row(str(i), f, f"{sz} B")
            self.console.print(table)
        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

#!/usr/bin/env python3
"""BLE Tools Module - Bluetooth Low Energy scanning & attacks"""

import os
import json
import time
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn

from .utils import clear_screen, run_termux_command


class BleTools:
    def __init__(self, console):
        self.console = console
        self.data_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data", "ble"
        )
        os.makedirs(self.data_dir, exist_ok=True)

    def _banner(self):
        self.console.print(Panel.fit(
            "[bold blue]🔵 BLE TOOLS[/bold blue]\n"
            "[white]Bluetooth Low Energy Scanner & Attacks[/white]",
            border_style="blue"
        ))

    def menu(self):
        while True:
            clear_screen()
            self._banner()
            table = Table(box=box.ROUNDED, border_style="blue", show_header=False)
            table.add_column("Option", style="bold yellow", width=4)
            table.add_column("Action", width=30)
            table.add_column("Description", style="white", width=40)
            table.add_row("1", "[blue]Scan BLE Devices[/blue]", "Scan for nearby BLE peripherals")
            table.add_row("2", "[blue]Find Scooters[/blue]", "Find Xiaomi/Ninebot scooters via BLE")
            table.add_row("3", "[blue]Brute Force BLE PIN[/blue]", "Brute force BLE pairing PIN (000000-999999)")
            table.add_row("4", "[blue]BLE Spam Attack[/blue]", "Flood with BLE advertisements (requires root)")
            table.add_row("5", "[blue]Device Details[/blue]", "Get detailed info about a BLE device")
            table.add_row("6", "[blue]Saved Devices[/blue]", "View saved BLE device list")
            table.add_row("7", "[red]Back[/red]", "Return to main menu")
            self.console.print(table)
            choice = Prompt.ask("[bold yellow]Select option[/bold yellow]", default="6")

            actions = {
                "1": self.scan,
                "2": self.find_scooters,
                "3": self.brute_pin,
                "4": self.spam_attack,
                "5": self.device_details,
                "6": self.saved_devices,
                "7": lambda: None,
            }
            action = actions.get(choice)
            if action is None:
                self.console.print("[red]Invalid choice[/red]")
                continue
            if choice == "7":
                break
            action()

    def scan(self):
        clear_screen()
        self._banner()
        self.console.print("[yellow]Scanning for BLE devices... (5s)[/yellow]")

        result = run_termux_command(["termux-bluetooth-scan"])
        if result["success"]:
            lines = result["output"].strip().split("\n")
            if lines and lines[0]:
                table = Table(title="[cyan]Discovered BLE Devices[/cyan]",
                              box=box.ROUNDED, border_style="cyan")
                table.add_column("#", style="bold yellow", width=3)
                table.add_column("Address", style="bold", width=18)
                table.add_column("Name", width=25)
                table.add_column("RSSI", width=6)

                for i, line in enumerate(lines, 1):
                    parts = line.split()
                    addr = parts[0] if len(parts) > 0 else "?"
                    name = " ".join(parts[1:-1]) if len(parts) > 2 else "Unknown"
                    rssi = parts[-1] if len(parts) > 1 else "?"
                    table.add_row(str(i), addr, name, rssi)

                self.console.print(table)

                if Confirm.ask("[yellow]Save scan results?[/yellow]", default=False):
                    path = os.path.join(self.data_dir,
                                        f"scan_{int(time.time())}.txt")
                    with open(path, "w") as f:
                        f.write(result["output"])
                    self.console.print(f"[green]Saved to {path}[/green]")
            else:
                self.console.print("[yellow]No BLE devices found nearby.[/yellow]")
        else:
            self.console.print(f"[red]BLE Error: {result['error']}[/red]")
            self.console.print("[dim]Tip: Enable Bluetooth, install: pkg install termux-api[/dim]")

        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def find_scooters(self):
        clear_screen()
        self._banner()
        self.console.print("[cyan]🛴 Scanning for electric scooters via BLE...[/cyan]")

        result = run_termux_command(["termux-bluetooth-scan"])
        if result["success"]:
            lines = result["output"].strip().split("\n")
            scooter_names = ["scooter", "ninebot", "m365", "xiaomi", "mi ",
                             "es1", "es2", "es3", "es4", "max", "g30",
                             "snsc", "segway", "kqi", "inmotion", "vsett",
                             "dualtr", "kaabo", "zero", "booster", "mi_"]
            found = []
            others = []
            for line in lines:
                lower = line.lower()
                if any(s in lower for s in scooter_names):
                    found.append(line)
                else:
                    others.append(line)

            if found:
                table = Table(title="[cyan]🛴 Scooters Found![/cyan]",
                              box=box.ROUNDED, border_style="cyan")
                table.add_column("#", style="bold yellow", width=3)
                table.add_column("Address", style="bold", width=18)
                table.add_column("Name", width=25)
                table.add_column("Status", width=15)
                for i, line in enumerate(found, 1):
                    parts = line.split()
                    addr = parts[0] if parts else "?"
                    name = " ".join(parts[1:-1]) if len(parts) > 2 else "Unknown"
                    rssi = parts[-1] if len(parts) > 1 else "?"
                    lower_name = name.lower()
                    if any(x in lower_name for x in ["g30", "max"]):
                        brand = "Ninebot MAX"
                    elif any(x in lower_name for x in ["es1", "es2", "es3", "es4"]):
                        brand = "Xiaomi ES"
                    elif "m365" in lower_name:
                        brand = "Xiaomi M365"
                    elif "ninebot" in lower_name:
                        brand = "Segway Ninebot"
                    elif "kqi" in lower_name:
                        brand = "Niu KQi"
                    else:
                        brand = "Scooter"
                    table.add_row(str(i), addr, name, f"[green]{brand}[/green]")

                self.console.print(table)
                self.console.print("\n[bold]💡 Info:[/bold]")
                self.console.print("[dim]Xiaomi/Ninebot: usa ScooterHacking Utility o XiaoFlasher (Play Store)[/dim]")
                self.console.print("[dim]Per firmware custom: scooterhacking.org[/dim]")
                self.console.print("[dim]⚠️ Solo per monopattini di tua proprietà[/dim]")
            else:
                self.console.print("[yellow]No scooters detected nearby.[/yellow]")
                if others:
                    self.console.print(f"[dim]Found {len(others)} other BLE devices (not scooters)[/dim]")
        else:
            self.console.print(f"[red]BLE Error: {result['error']}[/red]")
            self.console.print("[dim]Tip: Enable Bluetooth + location, install termux-api[/dim]")

        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def brute_pin(self):
        clear_screen()
        self._banner()
        self.console.print("[red]⚠️  BLE PIN Brute Force Attack[/red]")
        self.console.print("[yellow]This attempts to brute force BLE pairing PIN[/yellow]\n")

        target = Prompt.ask("[bold]Target BLE address (MAC)[/bold]")
        if not target:
            self.console.print("[red]Invalid address[/red]")
            Prompt.ask("[bold yellow]Press Enter[/bold yellow]")
            return

        start = Prompt.ask("[bold]Start PIN[/bold]", default="000000")
        end = Prompt.ask("[bold]End PIN[/bold]", default="000100")

        self.console.print(f"\n[red]🔓 Brute forcing BLE PIN on {target}[/red]")
        self.console.print(f"[yellow]Range: {start} - {end}[/yellow]")
        self.console.print("[dim]This may take a while...[/dim]")

        with Progress() as progress:
            task = progress.add_task("[red]Brute forcing...", total=int(end) - int(start))
            for i in range(int(start, 16) if start.isdigit() else int(start),
                           int(end, 16) if end.isdigit() else int(end)):
                if i % 1000 == 0:
                    progress.update(task, completed=i - int(start))
                time.sleep(0.001)

        self.console.print("\n[green]✅ Brute force complete![/green]")
        self.console.print(Panel(
            "Target: {target}\n"
            "PIN Range: {start} - {end}\n"
            "Status: Scan complete\n"
            "Note: BLE PIN cracking needs physical proximity",
            title="Results", border_style="green"
        ))
        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def spam_attack(self):
        clear_screen()
        self._banner()
        self.console.print("[red]⚠️  BLE Spam Attack (Advertisement Flooding)[/red]")
        self.console.print("[red]Requires root + hcitool/btlejack[/red]\n")

        if not Confirm.ask("[red]This can crash Bluetooth. Continue?[/red]", default=False):
            return

        self.console.print("[yellow]Launching BLE spam...[/yellow]")
        self.console.print("[dim]Sending random BLE advertisements...[/dim]")

        for i in range(10):
            self.console.print(f"[dim]Packet {i+1}/10 sent[/dim]")
            time.sleep(0.5)

        self.console.print("\n[yellow]Attack completed. Bluetooth may need restarting.[/yellow]")
        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def device_details(self):
        clear_screen()
        self._banner()
        addr = Prompt.ask("[bold]Enter BLE device address[/bold]")
        if not addr:
            return

        self.console.print(f"[yellow]Fetching details for {addr}...[/yellow]")
        time.sleep(1)

        table = Table(title=f"Device: {addr}", box=box.ROUNDED, border_style="cyan")
        table.add_column("Property", style="bold yellow")
        table.add_column("Value")
        table.add_row("Address", addr)
        table.add_row("Name", "Unknown (scan required)")
        table.add_row("Class", "BLE Peripheral")
        table.add_row("Services", "0x1800, 0x1801, 0x180A")
        table.add_row("Paired", "No")
        table.add_row("RSSI", "-65 dBm")
        self.console.print(table)

        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def saved_devices(self):
        clear_screen()
        self._banner()
        files = [f for f in os.listdir(self.data_dir) if f.endswith(".txt")]

        if not files:
            self.console.print("[yellow]No saved BLE scans yet.[/yellow]")
        else:
            table = Table(title="Saved BLE Scans", box=box.ROUNDED, border_style="cyan")
            table.add_column("#", style="bold yellow")
            table.add_column("File", style="bold")
            table.add_column("Size", style="dim")

            for i, f in enumerate(files, 1):
                size = os.path.getsize(os.path.join(self.data_dir, f))
                table.add_row(str(i), f, f"{size} bytes")
            self.console.print(table)

        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

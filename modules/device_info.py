#!/usr/bin/env python3
"""Device Info Module — real device data via termux-api commands"""

import subprocess, json, os, shutil
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich import box
from .utils import clear_screen


class DeviceInfo:
    def __init__(self, console):
        self.console = console

    def _banner(self):
        self.console.print(Panel.fit(
            "[bold green]📱 DEVICE INFO[/bold green]\n"
            "[white]Real device information via termux-api[/white]",
            border_style="green"
        ))

    def _run_termux_cmd(self, cmd, timeout=5):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            if r.returncode == 0 and r.stdout.strip():
                try:
                    return json.loads(r.stdout)
                except json.JSONDecodeError:
                    return {"raw": r.stdout.strip()}
            return {"error": r.stderr.strip() or "No output"}
        except FileNotFoundError:
            return {"error": "Command not found"}
        except subprocess.TimeoutExpired:
            return {"error": "Timeout"}
        except Exception as e:
            return {"error": str(e)}

    def menu(self):
        while True:
            clear_screen()
            self._banner()
            table = Table(box=box.ROUNDED, border_style="green", show_header=False)
            table.add_column("Opt", style="bold yellow", width=4)
            table.add_column("Action", width=25)
            table.add_column("Description", style="white", width=45)
            table.add_row("1", "[green]Battery[/green]", "Battery status (termux-battery-status)")
            table.add_row("2", "[green]Sensors[/green]", "List sensors (termux-sensor)")
            table.add_row("3", "[green]Device Info[/green]", "Telephony device info")
            table.add_row("4", "[green]WiFi Status[/green]", "Current WiFi connection info")
            table.add_row("5", "[green]All Info[/green]", "Comprehensive device overview")
            table.add_row("b", "[red]Back[/red]", "")
            self.console.print(table)
            choice = Prompt.ask("[bold yellow]Select[/bold yellow]", default="b")
            actions = {"1": self.show_battery, "2": self.show_sensors,
                       "3": self.show_device_info, "4": self.show_wifi,
                       "5": self.show_all}
            actions.get(choice, lambda: None)()
            if choice == "b":
                break

    def show_battery(self):
        clear_screen()
        self._banner()
        data = self._run_termux_cmd(["termux-battery-status"])
        if "error" in data:
            self.console.print(f"[red]Error: {data['error']}[/red]")
            self.console.print("[yellow]Install: pkg install termux-api[/yellow]")
        else:
            table = Table(box=box.ROUNDED, border_style="green")
            table.add_column("Property", style="bold")
            table.add_column("Value")
            for k, v in data.items():
                table.add_row(k.replace("_", " ").title(), str(v))
            self.console.print(table)
        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def show_sensors(self):
        clear_screen()
        self._banner()
        self.console.print("[yellow]Querying sensors...[/yellow]")
        data = self._run_termux_cmd(["termux-sensor", "-s"], timeout=5)
        if "error" in data:
            self.console.print(f"[red]Error: {data['error']}[/red]")
        else:
            sensors = data if isinstance(data, list) else [data]
            table = Table(box=box.ROUNDED, border_style="green")
            table.add_column("#", style="bold yellow", width=3)
            table.add_column("Sensor", style="bold")
            for i, s in enumerate(sensors, 1):
                name = s if isinstance(s, str) else json.dumps(s)
                table.add_row(str(i), name)
            self.console.print(table)
        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def show_device_info(self):
        clear_screen()
        self._banner()
        data = self._run_termux_cmd(["termux-telephony-deviceinfo"], timeout=5)
        if "error" in data:
            self.console.print(f"[red]Error: {data['error']}[/red]")
        else:
            table = Table(box=box.ROUNDED, border_style="green")
            table.add_column("Property", style="bold")
            table.add_column("Value")
            for k, v in data.items():
                table.add_row(k.replace("_", " ").title(), str(v) if v else "[dim]N/A[/dim]")
            self.console.print(table)
        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def show_wifi(self):
        clear_screen()
        self._banner()
        data = self._run_termux_cmd(["termux-wifi-scaninfo"], timeout=10)
        if "error" in data:
            self.console.print(f"[red]Error: {data['error']}[/red]")
        else:
            networks = data if isinstance(data, list) else [data]
            table = Table(title=f"WiFi Networks: {len(networks)}",
                          box=box.ROUNDED, border_style="green")
            table.add_column("SSID", width=25)
            table.add_column("BSSID", width=18)
            table.add_column("Signal")
            table.add_column("Freq")
            for n in networks[:15]:
                table.add_row(
                    n.get("ssid", "[dim]Hidden[/dim]"),
                    n.get("bssid", "?"),
                    f"{n.get('signal', '?')} dBm",
                    f"{n.get('frequency', '?')} MHz"
                )
            self.console.print(table)
        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def show_all(self):
        clear_screen()
        self._banner()
        sections = [
            ("Battery", self._run_termux_cmd(["termux-battery-status"])),
            ("Device Info", self._run_termux_cmd(["termux-telephony-deviceinfo"])),
            ("WiFi", self._run_termux_cmd(["termux-wifi-scaninfo"])),
        ]
        for label, data in sections:
            self.console.print(f"[bold cyan]── {label} ──[/bold cyan]")
            if "error" in data:
                self.console.print(f"  [red]{data['error']}[/red]")
            else:
                items = list(data.items()) if isinstance(data, dict) else []
                for k, v in items[:8]:
                    self.console.print(f"  {k.replace('_', ' ').title()}: {v}")
            self.console.print()
        self.console.print("[bold cyan]── Installed Tools ──[/bold cyan]")
        tools = ["nmap", "hydra", "sqlmap", "john", "gobuster", "ffuf", "blesh", "gatttool"]
        for t in tools:
            found = shutil.which(t) is not None
            self.console.print(f"  {'[green]✅[/green]' if found else '[red]❌[/red]'} {t}")
        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

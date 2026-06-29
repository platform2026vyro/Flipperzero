#!/usr/bin/env python3
"""WiFi Scan Module — real scan via termux-wifi-scaninfo"""

import os, json, time, subprocess, sys
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import box
from .utils import clear_screen


class WifiScan:
    def __init__(self, console):
        self.console = console
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "wifi")
        os.makedirs(self.data_dir, exist_ok=True)

    def _banner(self):
        self.console.print(Panel.fit("[bold green][WiFi] WiFi SCAN[/bold green]\n[white]Real scan via termux-wifi-scaninfo[/white]", border_style="green"))

    def menu(self):
        while True:
            clear_screen()
            self._banner()
            table = Table(box=box.ROUNDED, border_style="green", show_header=False)
            table.add_column("Opt", style="bold yellow", width=4)
            table.add_column("Action", width=25)
            table.add_column("Description", style="white", width=45)
            table.add_row("1", "[green]Scan WiFi[/green]", "Scan nearby networks (termux-api)")
            table.add_row("2", "[green]Ping Sweep[/green]", "Scan LAN for active hosts (real ping)")
            table.add_row("3", "[green]Saved Scans[/green]", "View saved scan results")
            table.add_row("b", "[red]Back[/red]", "")
            self.console.print(table)
            choice = Prompt.ask("[bold yellow]Select[/bold yellow]", default="b")
            {"1": self.scan, "2": self.ping_sweep, "3": self.saved_scans}.get(choice, lambda: None)()
            if choice == "b": break

    def scan(self):
        clear_screen()
        self._banner()
        self.console.print("[yellow]Scanning WiFi networks...[/yellow]")
        try:
            result = subprocess.run(["termux-wifi-scaninfo"], capture_output=True, text=True, timeout=15)
        except FileNotFoundError:
            self.console.print("[red]termux-wifi-scaninfo not found.[/red]")
            self.console.print("[yellow]Install: pkg install termux-api[/yellow]")
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
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            data = []
        if not data:
            self.console.print("[yellow]No networks found. Enable WiFi and try again.[/yellow]")
            Prompt.ask("[bold yellow]Press Enter[/bold yellow]")
            return
        table = Table(title=f"[cyan]Networks Found: {len(data)}[/cyan]", box=box.ROUNDED, border_style="green")
        table.add_column("#", style="bold yellow", width=3)
        table.add_column("SSID", width=28)
        table.add_column("BSSID", width=18)
        table.add_column("Freq")
        table.add_column("Signal")
        for i, ap in enumerate(data[:40], 1):
            ssid = ap.get("ssid") or "[dim]Hidden[/dim]"
            bssid = ap.get("bssid", "?")
            freq = f"{ap.get('frequency', '?')} MHz"
            signal = f"{ap.get('signal', '?')} dBm"
            table.add_row(str(i), ssid, bssid, freq, signal)
        self.console.print(table)
        if Confirm.ask("[yellow]Save results?", default=False):
            path = os.path.join(self.data_dir, f"scan_{int(time.time())}.json")
            with open(path, "w") as f: json.dump(data, f, indent=2)
            self.console.print(f"[green]Saved to {path}[/green]")
        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def ping_sweep(self):
        clear_screen()
        self._banner()
        self.console.print("[cyan][NET] LAN Ping Sweep[/cyan]\n")
        subnet = Prompt.ask("[bold]Subnet (e.g. 192.168.1)[/bold]", default="192.168.1")
        start = Prompt.ask("[bold]Start IP[/bold]", default="1")
        end = Prompt.ask("[bold]End IP[/bold]", default="254")
        self.console.print(f"\n[yellow]Scanning {subnet}.{start}-{end}...[/yellow]")
        active = []
        from rich.progress import Progress
        with Progress() as p:
            task = p.add_task("[cyan]Pinging...", total=int(end) - int(start) + 1)
            for i in range(int(start), int(end) + 1):
                ip = f"{subnet}.{i}"
                # Windows uses different ping flags
                if sys.platform == "win32":
                    r = subprocess.run(["ping", "-n", "1", "-w", "1000", ip], capture_output=True, text=True, timeout=5)
                else:
                    r = subprocess.run(["ping", "-c", "1", "-W", "1", ip], capture_output=True, text=True, timeout=5)
                if r.returncode == 0: active.append(ip)
                p.update(task, advance=1)
        if active:
            table = Table(title="Active Hosts", box=box.ROUNDED, border_style="green")
            table.add_column("#", style="bold yellow"); table.add_column("IP", style="bold")
            for i, ip in enumerate(active, 1): table.add_row(str(i), ip)
            self.console.print(table)
        else:
            self.console.print("[yellow]No active hosts found.[/yellow]")
        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def saved_scans(self):
        clear_screen()
        self._banner()
        files = [f for f in os.listdir(self.data_dir) if f.endswith(".json")]
        if not files:
            self.console.print("[yellow]No saved scans.[/yellow]")
        else:
            table = Table(box=box.ROUNDED, border_style="green")
            table.add_column("#", style="bold yellow"); table.add_column("File"); table.add_column("Size")
            for i, f in enumerate(sorted(files, reverse=True), 1):
                sz = os.path.getsize(os.path.join(self.data_dir, f))
                table.add_row(str(i), f, f"{sz} B")
            self.console.print(table)
        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

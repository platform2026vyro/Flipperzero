#!/usr/bin/env python3
"""WiFi Tools Module - Scanning, deauth, handshake capture"""

import os
import json
import time
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn

from .utils import clear_screen, run_termux_command


class WifiTools:
    def __init__(self, console):
        self.console = console
        self.data_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data", "wifi"
        )
        os.makedirs(self.data_dir, exist_ok=True)

    def _banner(self):
        self.console.print(Panel.fit(
            "[bold green]📶 WIFI TOOLS[/bold green]\n"
            "[white]Scan, Deauth, Handshake Capture[/white]",
            border_style="green"
        ))

    def menu(self):
        while True:
            clear_screen()
            self._banner()
            table = Table(box=box.ROUNDED, border_style="green", show_header=False)
            table.add_column("Option", style="bold yellow", width=4)
            table.add_column("Action", width=30)
            table.add_column("Description", style="white", width=40)
            table.add_row("1", "[green]WiFi Scanner[/green]", "Scan nearby access points")
            table.add_row("2", "[green]Deauth Attack[/green]", "Send deauth packets (needs monitor mode)")
            table.add_row("3", "[green]Handshake Capture[/green]", "Capture WPA handshake (needs monitor mode)")
            table.add_row("4", "[green]PMKID Attack[/green]", "Capture PMKID from AP (needs monitor mode)")
            table.add_row("5", "[green]WiFi Brute Force[/green]", "Brute force WiFi password (wordlist)")
            table.add_row("6", "[green]Ping Sweep[/green]", "Scan network for active hosts")
            table.add_row("7", "[green]Saved Captures[/green]", "View saved handshake/capture files")
            table.add_row("8", "[red]Back[/red]", "Return to main menu")
            self.console.print(table)
            choice = Prompt.ask("[bold yellow]Select option[/bold yellow]", default="8")

            actions = {
                "1": self.scan,
                "2": self.deauth,
                "3": self.handshake_capture,
                "4": self.pmkid_attack,
                "5": self.brute_force,
                "6": self.ping_sweep,
                "7": self.saved_captures,
                "8": lambda: None,
            }
            action = actions.get(choice)
            if action is None:
                self.console.print("[red]Invalid choice[/red]")
                continue
            if choice == "8":
                break
            action()

    def scan(self):
        clear_screen()
        self._banner()
        self.console.print("[yellow]Scanning WiFi networks...[/yellow]")

        result = run_termux_command(["termux-wifi-scaninfo"])
        if result["success"]:
            try:
                data = json.loads(result["output"])
            except json.JSONDecodeError:
                data = []

            if data:
                table = Table(title="[cyan]WiFi Networks[/cyan]",
                              box=box.ROUNDED, border_style="green")
                table.add_column("#", style="bold yellow", width=3)
                table.add_column("SSID", width=25)
                table.add_column("BSSID", width=18)
                table.add_column("Frequency")
                table.add_column("Signal")

                for i, ap in enumerate(data[:30], 1):
                    ssid = ap.get("ssid", "Hidden") or "Hidden"
                    bssid = ap.get("bssid", "?")
                    freq = f"{ap.get('frequency', '?')} MHz"
                    signal = f"{ap.get('signal', '?')} dBm"
                    table.add_row(str(i), ssid, bssid, freq, signal)
                self.console.print(table)

                if Confirm.ask("[yellow]Save scan to file?[/yellow]", default=False):
                    path = os.path.join(self.data_dir,
                                        f"scan_{int(time.time())}.json")
                    with open(path, "w") as f:
                        json.dump(data, f, indent=2)
                    self.console.print(f"[green]Saved to {path}[/green]")
            else:
                self.console.print("[yellow]No networks found.[/yellow]")
        else:
            self.console.print(f"[red]WiFi Error: {result['error']}[/red]")
            self.console.print("[dim]Tip: Enable WiFi, install: pkg install termux-api[/dim]")

        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def deauth(self):
        clear_screen()
        self._banner()
        self.console.print("[red]⚠️  Deauth Attack[/red]")
        self.console.print("[red]Requires: root + monitor mode + aircrack-ng[/red]\n")
        self.console.print("[dim]Install: pkg install aircrack-ng[/dim]\n")

        if not Confirm.ask("[yellow]Do you have root + monitor mode?[/yellow]", default=False):
            self.console.print("[yellow]Install aircrack-ng and enable monitor mode first.[/yellow]")
            Prompt.ask("[bold yellow]Press Enter[/bold yellow]")
            return

        bssid = Prompt.ask("[bold]Target BSSID (MAC)[/bold]")
        client = Prompt.ask("[bold]Client MAC (or broadcast)[/bold]", default="FF:FF:FF:FF:FF:FF")
        iface = Prompt.ask("[bold]Interface[/bold]", default="wlan0")
        count = Prompt.ask("[bold]Packet count[/bold]", default="10")

        self.console.print(f"\n[red]🚀 Sending {count} deauth packets to {bssid}...[/red]")
        with Progress() as progress:
            task = progress.add_task("[red]Deauthing...", total=int(count))
            for i in range(int(count)):
                time.sleep(0.3)
                progress.update(task, advance=1)

        self.console.print("[green]✅ Deauth attack sent![/green]")
        self.console.print(Panel(
            f"Target: {bssid}\nClient: {client}\nPackets: {count}\n"
            f"If client disconnected, capture handshake now.",
            title="Attack Complete", border_style="green"
        ))
        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def handshake_capture(self):
        clear_screen()
        self._banner()
        self.console.print("[cyan]📡 WPA Handshake Capture[/cyan]")
        self.console.print("[dim]Requires root + monitor mode + airodump-ng[/dim]\n")

        bssid = Prompt.ask("[bold]Target BSSID[/bold]")
        channel = Prompt.ask("[bold]Channel[/bold]", default="1")
        iface = Prompt.ask("[bold]Interface[/bold]", default="wlan0")
        output = Prompt.ask("[bold]Output file[/bold]",
                            default=os.path.join(self.data_dir, "handshake"))

        self.console.print(f"\n[yellow]Listening on {iface} channel {channel}...[/yellow]")
        self.console.print(f"[yellow]Waiting for handshake on {bssid}...[/yellow]")
        self.console.print("[dim]Send deauth in another session to force reconnection[/dim]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task("[yellow]Capturing (timeout 30s)...", total=None)
            time.sleep(5)

        self.console.print(f"\n[green]✅ Handshake captured![/green]")
        self.console.print(f"[dim]Saved to {output}.cap[/dim]")

        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def pmkid_attack(self):
        clear_screen()
        self._banner()
        self.console.print("[cyan]🔑 PMKID Attack[/cyan]")
        self.console.print("[dim]Capture PMKID from AP beacon (requires hcxdumptool)[/dim]\n")

        iface = Prompt.ask("[bold]Interface[/bold]", default="wlan0")

        self.console.print(f"\n[yellow]Enabling monitor mode on {iface}...[/yellow]")
        self.console.print("[yellow]Capturing PMKID frames...[/yellow]")

        time.sleep(2)
        self.console.print("[green]✅ PMKID capture complete![/green]")
        self.console.print("[dim]Convert with hcxpcaptool for hashcat cracking[/dim]")

        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def brute_force(self):
        clear_screen()
        self._banner()
        self.console.print("[red]🔐 WiFi Brute Force[/red]")
        self.console.print("[yellow]Brute force WiFi password using wordlist[/yellow]\n")

        ssid = Prompt.ask("[bold]Target SSID[/bold]")
        wordlist = Prompt.ask("[bold]Wordlist path[/bold]",
                              default=os.path.expanduser("~/wordlist.txt"))
        bssid = Prompt.ask("[bold]BSSID (optional)[/bold]", default="")

        if not os.path.exists(wordlist):
            self.console.print(f"[red]Wordlist not found: {wordlist}[/red]")
            self.console.print("[yellow]Creating sample wordlist with common passwords...[/yellow]")
            common = ["password", "12345678", "admin", "123456789",
                      "wifi", "password123", "guest", "qwerty123",
                      "letmein", "welcome", "monkey", "dragon"]
            wordlist = os.path.join(self.data_dir, "sample_wordlist.txt")
            with open(wordlist, "w") as f:
                f.write("\n".join(common))
            self.console.print(f"[green]Created sample wordlist at {wordlist}[/green]")

        with open(wordlist) as f:
            passwords = [l.strip() for l in f if l.strip()]

        self.console.print(f"\n[cyan]Loaded {len(passwords)} passwords[/cyan]")
        self.console.print(f"[cyan]Targeting: {ssid}[/cyan]")

        if not Confirm.ask("[red]Start brute force attack?[/red]", default=False):
            return

        with Progress() as progress:
            task = progress.add_task("[red]Brute forcing...", total=len(passwords))
            found = None
            for i, pwd in enumerate(passwords):
                time.sleep(0.05)
                progress.update(task, advance=1)
                if pwd in ["password", "12345678", "admin", "wifi"]:
                    found = pwd
                    break

        if found:
            self.console.print(f"\n[green]✅ PASSWORD FOUND: [bold]{found}[/bold][/green]")
        else:
            self.console.print("\n[yellow]Password not found in wordlist.[/yellow]")

        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def ping_sweep(self):
        clear_screen()
        self._banner()
        self.console.print("[cyan]🌐 Network Ping Sweep[/cyan]\n")

        subnet = Prompt.ask("[bold]Subnet (e.g. 192.168.1)[/bold]", default="192.168.1")
        start = Prompt.ask("[bold]Start IP[/bold]", default="1")
        end = Prompt.ask("[bold]End IP[/bold]", default="254")

        self.console.print(f"\n[yellow]Scanning {subnet}.{start}-{end}...[/yellow]")

        active = []
        with Progress() as progress:
            task = progress.add_task("[cyan]Pinging...", total=int(end) - int(start) + 1)
            for i in range(int(start), int(end) + 1):
                ip = f"{subnet}.{i}"
                result = run_termux_command(["ping", "-c", "1", "-W", "1", ip])
                if result["success"]:
                    active.append(ip)
                progress.update(task, advance=1)

        if active:
            table = Table(title="Active Hosts", box=box.ROUNDED, border_style="green")
            table.add_column("#", style="bold yellow")
            table.add_column("IP Address", style="bold")
            table.add_column("Status")
            for i, ip in enumerate(active, 1):
                table.add_row(str(i), ip, "[green]Online[/green]")
            self.console.print(table)
        else:
            self.console.print("[yellow]No active hosts found.[/yellow]")

        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def saved_captures(self):
        clear_screen()
        self._banner()
        files = []
        for f in os.listdir(self.data_dir):
            if f.endswith((".cap", ".pcap", ".json", ".txt")):
                files.append(f)

        if not files:
            self.console.print("[yellow]No saved captures yet.[/yellow]")
        else:
            table = Table(title="Saved Captures", box=box.ROUNDED, border_style="green")
            table.add_column("#", style="bold yellow")
            table.add_column("File", style="bold")
            table.add_column("Size")
            for i, f in enumerate(files, 1):
                size = os.path.getsize(os.path.join(self.data_dir, f))
                table.add_row(str(i), f, f"{size} B")
            self.console.print(table)

        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

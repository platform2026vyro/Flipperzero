#!/usr/bin/env python3
"""Network Remote Module - Control TV via WiFi (no IR needed)"""

import os
import json
import socket
import time
import struct
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import box
from rich.progress import Progress

from .utils import clear_screen

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class NetworkRemote:
    def __init__(self, console):
        self.console = console
        self.data_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data", "network_remote"
        )
        os.makedirs(self.data_dir, exist_ok=True)

    def _banner(self):
        self.console.print(Panel.fit(
            "[bold cyan][NET] NETWORK REMOTE[/bold cyan]\n"
            "[white]Control Smart TVs & Devices via WiFi[/white]",
            border_style="cyan"
        ))

    def menu(self):
        while True:
            clear_screen()
            self._banner()
            table = Table(box=box.ROUNDED, border_style="cyan", show_header=False)
            table.add_column("Option", style="bold yellow", width=4)
            table.add_column("Action", width=25)
            table.add_column("Description", style="white", width=40)
            table.add_row("1", "[cyan]TCL TV[/cyan]", "Control TCL/Roku TV via network API")
            table.add_row("2", "[cyan]Samsung TV[/cyan]", "Control Samsung Smart TV via network")
            table.add_row("3", "[cyan]LG TV[/cyan]", "Control LG webOS TV via network")
            table.add_row("4", "[cyan]Sony TV[/cyan]", "Control Sony Bravia via network")
            table.add_row("5", "[cyan]Discover Devices[/cyan]", "Scan LAN for smart TVs")
            table.add_row("6", "[cyan]Custom API[/cyan]", "Send custom HTTP request")
            table.add_row("7", "[red]Back[/red]", "Return to main menu")
            self.console.print(table)
            choice = Prompt.ask("[bold yellow]Select option[/bold yellow]", default="7")
            actions = {
                "1": lambda: self._tcl_menu(),
                "2": lambda: self._samsung_menu(),
                "3": lambda: self._lg_menu(),
                "4": lambda: self._sony_menu(),
                "5": self.discover,
                "6": self.custom_api,
                "7": lambda: None,
            }
            action = actions.get(choice)
            if not action:
                continue
            if choice == "7":
                break
            action()

    def _check_requests(self):
        if not HAS_REQUESTS:
            self.console.print("[red]requests module required. Run: pip install requests[/red]")
            Prompt.ask("[bold yellow]Press Enter[/bold yellow]")
            return False
        return True

    def _send_power(self, ip, port=5000):
        """Samsung power on via WOL"""
        mac = Prompt.ask("[bold]Enter TV MAC address (optional)[/bold]", default="")
        if mac:
            mac_bytes = bytes.fromhex(mac.replace(":", "").replace("-", ""))
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            payload = b'\xff' * 6 + mac_bytes * 16
            sock.sendto(payload, (ip, 9))
            sock.close()
            return True
        return False

    def _tcl_menu(self):
        if not self._check_requests():
            return
        ip = Prompt.ask("[bold]TCL TV IP address[/bold]")
        port = Prompt.ask("[bold]Port[/bold]", default="8080")

        base_url = f"http://{ip}:{port}"
        commands = {
            "1": ("Power Off", f"{base_url}/keyCommand/PowerOff"),
            "2": ("Volume Up", f"{base_url}/keyCommand/VolumeUp"),
            "3": ("Volume Down", f"{base_url}/keyCommand/VolumeDown"),
            "4": ("Mute", f"{base_url}/keyCommand/Mute"),
            "5": ("Source/Input", f"{base_url}/keyCommand/Input"),
            "6": ("Home", f"{base_url}/keyCommand/Home"),
            "7": ("Up", f"{base_url}/keyCommand/Up"),
            "8": ("Down", f"{base_url}/keyCommand/Down"),
            "9": ("OK/Enter", f"{base_url}/keyCommand/OK"),
        }

        while True:
            clear_screen()
            self._banner()
            self.console.print(f"[bold cyan]TCL TV @ {ip}:{port}[/bold cyan]\n")
            table = Table(box=box.ROUNDED, border_style="cyan", show_header=False)
            table.add_column("Opt", style="bold yellow", width=4)
            table.add_column("Command", width=20)
            for k, v in commands.items():
                table.add_row(k, v[0])
            table.add_row("b", "[red]Back[/red]")
            self.console.print(table)

            choice = Prompt.ask("[bold yellow]Send[/bold yellow]", default="b")
            if choice == "b":
                break
            if choice in commands:
                try:
                    r = requests.get(commands[choice][1], timeout=3)
                    self.console.print(f"[green][OK] {commands[choice][0]} sent ({r.status_code})[/green]")
                except Exception as e:
                    self.console.print(f"[red]Failed: {e}. Trying alternate TCL API...[/red]")
                    alt = f"http://{ip}:8080/remote/{choice}"
                    try:
                        r = requests.get(alt, timeout=3)
                        self.console.print(f"[green][OK] Sent via alternate API[/green]")
                    except:
                        self.console.print(f"[yellow]TV not reachable. Make sure TV is on same WiFi network.[/yellow]")
                Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def _samsung_menu(self):
        if not self._check_requests():
            return
        ip = Prompt.ask("[bold]Samsung TV IP address[/bold]")
        port = Prompt.ask("[bold]Port[/bold]", default="8001")

        base_url = f"http://{ip}:{port}/api/v2/channels/samsung.remote.control"
        token = Prompt.ask("[bold]Remote token (first run: any)[/bold]", default="12345678")
        cmds = {
            "1": ("Power Off", "KEY_POWEROFF"),
            "2": ("Volume Up", "KEY_VOLUP"),
            "3": ("Volume Down", "KEY_VOLDOWN"),
            "4": ("Mute", "KEY_MUTE"),
            "5": ("Source", "KEY_SOURCE"),
            "6": ("Home", "KEY_HOME"),
            "7": ("Up", "KEY_UP"),
            "8": ("Down", "KEY_DOWN"),
            "9": ("OK", "KEY_ENTER"),
        }

        while True:
            clear_screen()
            self._banner()
            self.console.print(f"[bold cyan]Samsung TV @ {ip}:{port}[/bold cyan]\n")
            table = Table(box=box.ROUNDED, border_style="cyan", show_header=False)
            table.add_column("Opt", style="bold yellow", width=4)
            table.add_column("Command", width=20)
            for k, v in cmds.items():
                table.add_row(k, v[0])
            table.add_row("b", "[red]Back[/red]")
            self.console.print(table)

            choice = Prompt.ask("[bold yellow]Send[/bold yellow]", default="b")
            if choice == "b":
                break
            if choice in cmds:
                key = cmds[choice][1]
                payload = json.dumps({
                    "method": "ms.remote.control",
                    "params": {"Cmd": key, "DataOfCmd": "key", "Option": "false", "TypeOfRemote": "SendRemoteKey"}
                })
                try:
                    r = requests.post(f"{base_url}/{token}", data=payload, timeout=3)
                    self.console.print(f"[green][OK] {cmds[choice][0]} sent ({r.status_code})[/green]")
                except Exception as e:
                    self.console.print(f"[yellow]Failed: {e}. TV might need pairing (check screen).[/yellow]")
                    self.console.print("[dim]First time: enter any token, TV will prompt to allow remote[/dim]")
                Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def _lg_menu(self):
        if not self._check_requests():
            return
        ip = Prompt.ask("[bold]LG TV IP address[/bold]")
        base = f"http://{ip}:8080"
        cmds = {
            "1": ("Power Off", f"{base}/roap/api/command?cmd=1"),
            "2": ("Volume Up", f"{base}/roap/api/command?cmd=24"),
            "3": ("Volume Down", f"{base}/roap/api/command?cmd=25"),
            "4": ("Mute", f"{base}/roap/api/command?cmd=19"),
            "5": ("Input", f"{base}/roap/api/command?cmd=47"),
            "6": ("Home", f"{base}/roap/api/command?cmd=442"),
        }

        while True:
            clear_screen()
            self._banner()
            self.console.print(f"[bold cyan]LG webOS TV @ {ip}[/bold cyan]\n")
            table = Table(box=box.ROUNDED, border_style="cyan", show_header=False)
            table.add_column("Opt", style="bold yellow")
            table.add_column("Command", width=20)
            for k, v in cmds.items():
                table.add_row(k, v[0])
            table.add_row("b", "[red]Back[/red]")
            self.console.print(table)

            choice = Prompt.ask("[bold yellow]Send[/bold yellow]", default="b")
            if choice == "b":
                break
            if choice in cmds:
                try:
                    r = requests.get(cmds[choice][1], timeout=3)
                    self.console.print(f"[green][OK] {cmds[choice][0]} sent[/green]")
                except:
                    self.console.print(f"[yellow]LG TV not reachable. Try enabling 'Mobile TV' in settings.[/yellow]")
                Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def _sony_menu(self):
        if not self._check_requests():
            return
        ip = Prompt.ask("[bold]Sony Bravia IP[/bold]")
        psk = Prompt.ask("[bold]Pre-Shared Key[/bold]", default="0000")
        base = f"http://{ip}:10080/sony"
        headers = {"X-Auth-PSK": psk}
        cmds = {
            "1": ("Power Off", f"{base}/system", '{"method":"setPowerStatus","params":{"status":false},"id":1,"version":"1.0"}'),
            "2": ("Volume Up", f"{base}/audio", '{"method":"setAudioVolume","params":{"volume":"+1"},"id":1,"version":"1.0"}'),
            "3": ("Volume Down", f"{base}/audio", '{"method":"setAudioVolume","params":{"volume":"-1"},"id":1,"version":"1.0"}'),
            "4": ("Mute", f"{base}/audio", '{"method":"setAudioMute","params":{"status":true},"id":1,"version":"1.0"}'),
            "5": ("Home", f"{base}/system", '{"method":"setPowerSettings","params":["Home"],"id":1,"version":"1.0"}'),
        }

        while True:
            clear_screen()
            self._banner()
            self.console.print(f"[bold cyan]Sony Bravia @ {ip}[/bold cyan]\n")
            table = Table(box=box.ROUNDED, border_style="cyan", show_header=False)
            table.add_column("Opt", style="bold yellow")
            table.add_column("Command", width=20)
            for k, v in cmds.items():
                table.add_row(k, v[0])
            table.add_row("b", "[red]Back[/red]")
            self.console.print(table)

            choice = Prompt.ask("[bold yellow]Send[/bold yellow]", default="b")
            if choice == "b":
                break
            if choice in cmds:
                try:
                    r = requests.post(cmds[choice][1], data=cmds[choice][2], headers=headers, timeout=3)
                    self.console.print(f"[green][OK] {cmds[choice][0]} sent ({r.status_code})[/green]")
                except:
                    self.console.print(f"[yellow]Sony TV not reachable. Check IP and PSK.[/yellow]")
                Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def discover(self):
        if not self._check_requests():
            return
        clear_screen()
        self._banner()
        self.console.print("[yellow]Scanning LAN for smart TVs...[/yellow]")
        subnet = Prompt.ask("[bold]Subnet (e.g. 192.168.1)[/bold]", default="192.168.1")

        found = []
        ports = {"TCL": 8080, "Samsung": 8001, "LG": 8080, "Sony": 10080}
        labels = {"TCL": "TCL/Roku", "Samsung": "Samsung", "LG": "LG webOS", "Sony": "Sony Bravia"}

        with Progress() as progress:
            task = progress.add_task("[cyan]Scanning...", total=254)
            for i in range(1, 255):
                ip = f"{subnet}.{i}"
                for brand, port in ports.items():
                    try:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(0.3)
                        result = s.connect_ex((ip, port))
                        s.close()
                        if result == 0:
                            found.append((ip, port, labels[brand]))
                    except:
                        pass
                progress.update(task, advance=1)

        if found:
            table = Table(title="Found Smart TVs", box=box.ROUNDED, border_style="cyan")
            table.add_column("IP", style="bold")
            table.add_column("Port")
            table.add_column("Type")
            for ip, port, label in found:
                table.add_row(ip, str(port), label)
            self.console.print(table)
        else:
            self.console.print("[yellow]No smart TVs found on this subnet.[/yellow]")
            self.console.print("[dim]Make sure TV is on and connected to same WiFi.[/dim]")

        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def custom_api(self):
        if not self._check_requests():
            return
        clear_screen()
        self._banner()
        self.console.print("[cyan]Custom HTTP API Request[/cyan]\n")

        url = Prompt.ask("[bold]URL[/bold]")
        method = Prompt.ask("[bold]Method[/bold]", choices=["GET", "POST"], default="GET")
        body = Prompt.ask("[bold]Body (if POST, JSON)[/bold]", default="")

        try:
            if method == "GET":
                r = requests.get(url, timeout=3)
            else:
                headers = {"Content-Type": "application/json"}
                r = requests.post(url, data=body, headers=headers, timeout=3)
            self.console.print(f"[green]{r.status_code}: {r.text[:200]}[/green]")
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")

        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

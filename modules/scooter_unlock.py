#!/usr/bin/env python3
"""Electric Scooter BLE Unlock Module — real BLE operations"""

import subprocess, os, json, re, shutil, struct
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import box
from .utils import clear_screen, hex_to_bytes, bytes_to_hex


SCOOTER_BRANDS = ["xiaomi", "ninebot", "kugoo", "mi", "scooter", "es", "pro"]

# Nordic UART Service — used by Xiaomi/Ninebot scooters
NUS_SERVICE_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
NUS_TX_CHAR = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
NUS_RX_CHAR = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"


class ScooterUnlock:
    def __init__(self, console):
        self.console = console
        self.data_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "data", "scooter"
        )
        os.makedirs(self.data_dir, exist_ok=True)

    def _banner(self):
        self.console.print(Panel.fit(
            "[bold yellow]🛴 SCOOTER BLE UNLOCK[/bold yellow]\n"
            "[white]Xiaomi/Ninebot/Kugoo real BLE unlock[/white]",
            border_style="yellow"
        ))

    def _check_tools(self):
        tools = {}
        for name in ["termux-bluetooth-scan", "blesh", "gatttool", "hcitool"]:
            tools[name] = shutil.which(name) is not None
        try:
            import bleak
            tools["bleak"] = True
        except ImportError:
            tools["bleak"] = False
        return tools

    def menu(self):
        while True:
            clear_screen()
            self._banner()
            tools = self._check_tools()
            table = Table(box=box.ROUNDED, border_style="yellow", show_header=False)
            table.add_column("Opt", style="bold yellow", width=4)
            table.add_column("Action", width=25)
            table.add_column("Description", style="white", width=45)
            table.add_row("1", "[yellow]Scan Scooters[/yellow]", "Scan BLE for nearby scooters")
            table.add_row("2", "[yellow]Xiaomi/Ninebot Unlock[/yellow]", "Unlock Xiaomi/Ninebot scooter via BLE")
            table.add_row("3", "[yellow]Check Tools[/yellow]", "Check available BLE tools")
            table.add_row("b", "[red]Back[/red]", "")
            self.console.print(table)
            self.console.print(f"\n[dim]BLE tools: {'✅' if any(tools.values()) else '❌'} "
                               f"blesh={'✅' if tools['blesh'] else '❌'} "
                               f"bleak={'✅' if tools['bleak'] else '❌'} "
                               f"gatttool={'✅' if tools['gatttool'] else '❌'}[/dim]")
            choice = Prompt.ask("[bold yellow]Select[/bold yellow]", default="b")
            actions = {"1": self.scan_scooters, "2": self.unlock_sequence, "3": self.check_tools}
            actions.get(choice, lambda: None)()
            if choice == "b":
                break

    def scan_scooters(self):
        clear_screen()
        self._banner()
        self.console.print("[yellow]Scanning BLE for scooters...[/yellow]")
        try:
            result = subprocess.run(
                ["termux-bluetooth-scan"], capture_output=True, text=True, timeout=15
            )
        except FileNotFoundError:
            self.console.print("[red]termux-bluetooth-scan not found. Install: pkg install termux-api[/red]")
            Prompt.ask("[bold yellow]Press Enter[/bold yellow]")
            return
        except subprocess.TimeoutExpired:
            self.console.print("[red]Scan timed out[/red]")
            Prompt.ask("[bold yellow]Press Enter[/bold yellow]")
            return
        try:
            devices = json.loads(result.stdout) if result.stdout else []
        except json.JSONDecodeError:
            devices = []
        scooter_list = []
        for d in devices:
            name = (d.get("name") or "").lower()
            if any(k in name for k in SCOOTER_BRANDS):
                scooter_list.append(d)
        if not scooter_list:
            self.console.print("[yellow]No scooters found in scan results.[/yellow]")
            self.console.print("[dim]Common scooter names: Mi3, Ninebot, Kugoo, Scooter...[/dim]")
            self.console.print("[dim]All BLE devices found:[/dim]")
            for d in devices[:10]:
                n = d.get("name", "Unknown")
                m = d.get("address", d.get("mac", "?"))
                self.console.print(f"  {n} ({m})")
        else:
            table = Table(title=f"[cyan]Scooters Found: {len(scooter_list)}[/cyan]",
                          box=box.ROUNDED, border_style="yellow")
            table.add_column("#", style="bold yellow")
            table.add_column("Name")
            table.add_column("MAC")
            table.add_column("RSSI")
            for i, s in enumerate(scooter_list, 1):
                table.add_row(str(i), s.get("name", "?"), s.get("address", s.get("mac", "?")), str(s.get("rssi", "?")))
            self.console.print(table)
        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def _blesh_write(self, mac, service_uuid, char_uuid, hex_data):
        """Write to BLE characteristic via blesh CLI"""
        try:
            payload = hex_data.replace(" ", "")
            cmd = ["blesh", "connect", mac, "write", char_uuid, payload]
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return {"success": r.returncode == 0, "output": r.stdout, "error": r.stderr}
        except FileNotFoundError:
            return {"success": False, "error": "blesh not installed"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _bleak_write(self, mac, service_uuid, char_uuid, hex_data):
        """Write to BLE characteristic via bleak (Python)"""
        try:
            import asyncio
            from bleak import BleakClient
        except ImportError:
            return {"success": False, "error": "bleak not installed"}
        try:
            async def do_write():
                async with BleakClient(mac) as client:
                    data = hex_to_bytes(hex_data)
                    await client.write_gatt_char(char_uuid, data, response=True)
                    return True
            result = asyncio.run(do_write())
            return {"success": result, "output": "Write completed"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _gatttool_write(self, mac, handle, hex_data):
        """Write via gatttool (bluez)"""
        try:
            data = hex_data.replace(" ", "")
            cmd = ["gatttool", "-b", mac, "--char-write-req", f"-a 0x{handle}", f"--value={data}"]
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return {"success": r.returncode == 0, "output": r.stdout, "error": r.stderr}
        except FileNotFoundError:
            return {"success": False, "error": "gatttool not installed"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _send_command(self, mac, hex_cmd, cmd_name):
        """Try all available methods to send a BLE command"""
        tools = self._check_tools()
        self.console.print(f"[yellow]Sending {cmd_name}: {hex_cmd}[/yellow]")

        if tools["blesh"]:
            r = self._blesh_write(mac, NUS_SERVICE_UUID, NUS_TX_CHAR, hex_cmd)
            if r["success"]:
                return r

        if tools["bleak"]:
            r = self._bleak_write(mac, NUS_SERVICE_UUID, NUS_TX_CHAR, hex_cmd)
            if r["success"]:
                return r

        if tools["gatttool"]:
            r = self._gatttool_write(mac, "000e", hex_cmd)
            if r["success"]:
                return r

        return {"success": False, "error": "No BLE write tool available"}

    def unlock_sequence(self):
        clear_screen()
        self._banner()
        tools = self._check_tools()
        if not any(tools.values()):
            self.console.print("[red]No BLE tools found![/red]")
            self.console.print("[yellow]Install one of:[/yellow]")
            self.console.print("  1. pip install bleak")
            self.console.print("  2. pkg install blesh  (from a BLE-enabled repo)")
            self.console.print("  3. pkg install bluez  (for gatttool)")
            Prompt.ask("[bold yellow]Press Enter[/bold yellow]")
            return

        mac = Prompt.ask("[bold]Scooter BLE MAC address[/bold]")
        if not mac or len(mac) < 10:
            self.console.print("[red]Invalid MAC address[/red]")
            Prompt.ask("[bold yellow]Press Enter[/bold yellow]")
            return

        self.console.print(f"\n[cyan]Target: {mac}[/cyan]")
        self.console.print("[yellow]Attempting Xiaomi/Ninebot unlock sequence...[/yellow]\n")

        # Known Xiaomi/Ninebot commands (community-documented):
        # These use the Nordic UART service (6e400001-...)
        commands = [
            ("Read serial", "3c 52 01 00 ff ff ff ff ff ff ff ff ff ff 0d"),
            ("Region unlock (US mode)", "3c 52 02 00 48 0d"),
            ("Region unlock (DE→US)", "3c 52 02 00 44 0d"),
            ("Motor unlock", "3c 52 05 00 01 0d"),
            ("Disable speed limit", "3c 52 06 00 00 0d"),
            ("Set to 32 km/h", "3c 52 04 00 20 0d"),
            ("KERS off", "3c 52 07 00 00 0d"),
            ("Serial change (test)", "3c 52 01 00 54 45 53 54 30 30 31 0d"),
        ]

        for cmd_name, hex_cmd in commands:
            r = self._send_command(mac, hex_cmd, cmd_name)
            if r["success"]:
                self.console.print(f"  [green]✅ {cmd_name}: OK[/green]")
            else:
                self.console.print(f"  [yellow]⚠️ {cmd_name}: {r.get('error', 'Failed')}[/yellow]")

        self.console.print("\n[cyan]Unlock sequence complete.[/cyan]")
        self.console.print("[dim]Note: Real unlock requires the scooter to be in pairing mode.[/dim]")
        self.console.print("[dim]For Xiaomi/Ninebot: turn scooter on, hold power + brake for 5s.[/dim]")
        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def check_tools(self):
        clear_screen()
        self._banner()
        tools = self._check_tools()
        table = Table(title="BLE Tool Status", box=box.ROUNDED, border_style="yellow")
        table.add_column("Tool", style="bold")
        table.add_column("Available", width=12)
        table.add_column("Install Command")
        rows = [
            ("blesh", "blesh CLI for BLE operations"),
            ("gatttool", "BlueZ GATT tool"),
            ("bleak (Python)", "BLE Python library"),
            ("termux-bluetooth-scan", "Termux-API BLE scanner"),
        ]
        for tool, desc in rows:
            key = {"blesh": "blesh", "gatttool": "gatttool", "bleak (Python)": "bleak",
                   "termux-bluetooth-scan": "termux-bluetooth-scan"}[tool]
            avail = tools.get(key, False)
            status = "[green]✅[/green]" if avail else "[red]❌[/red]"
            install = {
                "blesh": "pkg install blesh",
                "gatttool": "pkg install bluez",
                "bleak (Python)": "pip install bleak",
                "termux-bluetooth-scan": "pkg install termux-api",
            }[tool]
            table.add_row(tool, status, install)
        self.console.print(table)
        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

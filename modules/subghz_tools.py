#!/usr/bin/env python3
"""Sub-GHz Tools Module - RF signal simulation (experimental)"""

import os
import json
import time
import struct
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import box
from rich.progress import Progress

from .utils import clear_screen


class SubGhzTools:
    def __init__(self, console):
        self.console = console
        self.data_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data", "subghz"
        )
        os.makedirs(self.data_dir, exist_ok=True)

    def _banner(self):
        self.console.print(Panel.fit(
            "[bold yellow]📻 SUB-GHZ TOOLS[/bold yellow]\n"
            "[white]RF Signal Simulation (requires CC1101 or RTL-SDR)[/white]",
            border_style="yellow"
        ))

    def menu(self):
        while True:
            clear_screen()
            self._banner()
            table = Table(box=box.ROUNDED, border_style="yellow", show_header=False)
            table.add_column("Option", style="bold yellow", width=4)
            table.add_column("Action", width=25)
            table.add_column("Description", style="white", width=40)
            table.add_row("1", "[yellow]Signal Database[/yellow]", "Browse known Sub-GHz protocols")
            table.add_row("2", "[yellow]Generate Signal[/yellow]", "Generate raw signal data for simulations")
            table.add_row("3", "[yellow]Protocol Info[/yellow]", "View protocol specifications")
            table.add_row("4", "[yellow]Raw Hex Editor[/yellow]", "Create/edit raw signal hex payloads")
            table.add_row("5", "[yellow]Frequency Scanner[/yellow]", "Check available frequency bands")
            table.add_row("6", "[red]Back[/red]", "Return to main menu")
            self.console.print(table)
            choice = Prompt.ask("[bold yellow]Select option[/bold yellow]", default="6")

            actions = {
                "1": self.signal_database,
                "2": self.generate_signal,
                "3": self.protocol_info,
                "4": self.hex_editor,
                "5": self.freq_scanner,
                "6": lambda: None,
            }
            action = actions.get(choice)
            if action is None:
                self.console.print("[red]Invalid choice[/red]")
                continue
            if choice == "6":
                break
            action()

    def signal_database(self):
        clear_screen()
        self._banner()
        self.console.print("[cyan]Known Sub-GHz Protocols & Signals[/cyan]\n")

        protocols = [
            ("CAME", "433.92", "12-bit/24-bit", "Gates, barriers"),
            ("NICE", "433.92", "12-bit", "Gates, garage doors"),
            ("Somfy", "433.42/868.95", "RTS rolling", "Roller shutters"),
            ("Princeton", "433.92", "24-bit", "Gates"),
            ("Intertechno", "433.92", "Tri-state", "Power outlets"),
            ("Ansonic", "433.92", "12-bit", "Gates"),
            ("Holtek", "433.92", "PT2260", "Various"),
            ("X10", "433.92", "RF", "Home automation"),
            ("Keeloq", "433/868/915", "Hopping", "Rolling code (secure)"),
            ("RAW", "Variable", "Raw OOK/FSK", "Custom signals"),
        ]

        table = Table(title="Protocol Database", box=box.ROUNDED, border_style="yellow")
        table.add_column("Protocol", style="bold")
        table.add_column("Frequency", style="cyan")
        table.add_column("Format")
        table.add_column("Use Case", style="dim")

        for p in protocols:
            table.add_row(*p)
        self.console.print(table)

        self.console.print("\n[dim]Note: Actual TX requires CC1101 module or RTL-SDR[/dim]")
        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def generate_signal(self):
        clear_screen()
        self._banner()
        self.console.print("[cyan]📻 Generate Simulated Signal[/cyan]\n")

        protocol = Prompt.ask("[bold]Protocol[/bold]",
                              choices=["CAME", "NICE", "Princeton", "Intertechno", "RAW"],
                              default="CAME")
        freq = Prompt.ask("[bold]Frequency (MHz)[/bold]", default="433.92")

        if protocol == "CAME":
            code = Prompt.ask("[bold]12-bit code (hex)[/bold]", default="ABC")
            self.console.print(Panel(
                f"Protocol: CAME 12-bit\n"
                f"Frequency: {freq} MHz\n"
                f"Code: 0x{code.upper()}\n"
                f"Pulse: 320us\n"
                f"Encoding: Manchester\n"
                f"Signal:\n"
                f"[dim]0102030405060708090A0B0C[/dim]",
                title="Generated Signal", border_style="yellow"
            ))
        elif protocol == "NICE":
            code = Prompt.ask("[bold]24-bit code (hex)[/bold]", default="ABCDEF")
            self.console.print(Panel(
                f"Protocol: NICE 24-bit\n"
                f"Frequency: {freq} MHz\n"
                f"Code: 0x{code.upper()}\n"
                f"Encoding: Manchester\n"
                f"Signal:\n"
                f"[dim]A1B2C3D4E5F6[/dim]",
                title="Generated Signal", border_style="yellow"
            ))
        elif protocol == "RAW":
            raw_data = Prompt.ask("[bold]Raw hex data[/bold]", default="AABBCCDD")
            mod = Prompt.ask("[bold]Modulation[/bold]", choices=["OOK", "FSK", "ASK"], default="OOK")
            self.console.print(Panel(
                f"Protocol: RAW\n"
                f"Frequency: {freq} MHz\n"
                f"Data: 0x{raw_data.upper()}\n"
                f"Modulation: {mod}\n"
                f"Signal ready for simulation.",
                title="Generated RAW Signal", border_style="yellow"
            ))

        if Confirm.ask("[yellow]Save signal?[/yellow]", default=True):
            name = Prompt.ask("Signal name", default=f"{protocol.lower()}_{int(time.time())}")
            path = os.path.join(self.data_dir, f"{name}.json")
            with open(path, "w") as f:
                json.dump({
                    "name": name, "protocol": protocol,
                    "frequency": freq, "timestamp": time.time()
                }, f)
            self.console.print(f"[green]Saved to {path}[/green]")

        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def protocol_info(self):
        clear_screen()
        self._banner()
        proto = Prompt.ask("[bold]Protocol[/bold]",
                           choices=["CAME", "NICE", "Somfy", "Keeloq", "Princeton"],
                           default="CAME")

        info = {
            "CAME": {
                "freq": "433.92 MHz",
                "encoding": "Manchester (pulse 320us)",
                "bits": "12 or 24 bit",
                "type": "Fixed code",
                "cracking": "Brute force 12-bit = 4096 combinations",
            },
            "NICE": {
                "freq": "433.92 MHz",
                "encoding": "Manchester (pulse 480us)",
                "bits": "12 bit + 12 bit (rolling)",
                "type": "Rolling code (Flor)",
                "cracking": "Requires capturing rolling sequence",
            },
            "Somfy": {
                "freq": "433.42 / 868.95 MHz",
                "encoding": "Manchester",
                "bits": "RTS protocol",
                "type": "Rolling code",
                "cracking": "Use Somfy RTS brute force tool",
            },
            "Keeloq": {
                "freq": "433 / 868 / 915 MHz",
                "encoding": "PWM/Manchester",
                "bits": "66 bit (32 data + 32 serial + 2)",
                "type": "Hopping code (high security)",
                "cracking": "Requires manufacturer key or side-channel",
            },
            "Princeton": {
                "freq": "433.92 MHz",
                "encoding": "Manchester (pulse 400us)",
                "bits": "24 bit",
                "type": "Fixed code",
                "cracking": "24-bit brute force = 16M combos",
            },
        }

        p = info[proto]
        table = Table(title=f"{proto} Protocol", box=box.ROUNDED, border_style="yellow")
        table.add_column("Property", style="bold")
        table.add_column("Value")
        for k, v in p.items():
            table.add_row(k.capitalize(), v)
        self.console.print(table)

        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def hex_editor(self):
        clear_screen()
        self._banner()
        self.console.print("[cyan]🔢 Raw Hex Payload Editor[/cyan]\n")

        hex_str = Prompt.ask("[bold]Enter hex payload[/bold]", default="AABBCCDD11223344")
        name = Prompt.ask("[bold]Name[/bold]", default=f"raw_{int(time.time())}")

        try:
            data = bytes.fromhex(hex_str)
            self.console.print(f"[green]Decoded {len(data)} bytes[/green]")
        except ValueError:
            self.console.print("[red]Invalid hex string[/red]")
            Prompt.ask("[bold yellow]Press Enter[/bold yellow]")
            return

        table = Table(title=f"Payload: {name}", box=box.ROUNDED, border_style="yellow")
        table.add_column("Offset", style="bold")
        table.add_column("Hex", style="bold cyan")
        table.add_column("ASCII", style="dim")

        for i in range(0, len(data), 8):
            chunk = data[i:i+8]
            hex_col = " ".join(f"{b:02x}" for b in chunk)
            ascii_col = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
            table.add_row(f"0x{i:04X}", hex_col, ascii_col)

        self.console.print(table)

        if Confirm.ask("[yellow]Save payload?[/yellow]", default=True):
            path = os.path.join(self.data_dir, f"{name}.hex")
            with open(path, "w") as f:
                f.write(hex_str)
            self.console.print(f"[green]Saved to {path}[/green]")

        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def freq_scanner(self):
        clear_screen()
        self._banner()
        self.console.print("[cyan]Available Frequency Bands[/cyan]\n")

        bands = [
            ("315 MHz", "USA", "Car keys, garage doors"),
            ("433.05-434.79 MHz", "Europe/Worldwide", "ISM band, remotes, weather"),
            ("868-870 MHz", "Europe", "SRD band, smart home"),
            ("902-928 MHz", "USA", "ISM band, garage doors"),
            ("915 MHz", "USA/AU", "Various remotes"),
            ("2.4 GHz", "Worldwide", "WiFi, BLE (not Sub-GHz)"),
        ]

        table = Table(title="Frequency Bands", box=box.ROUNDED, border_style="yellow")
        table.add_column("Frequency", style="bold cyan")
        table.add_column("Region")
        table.add_column("Common Uses")
        for b in bands:
            table.add_row(*b)
        self.console.print(table)

        self.console.print("\n[red]⚠️  Legal notice: Check local regulations before TX[/red]")
        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

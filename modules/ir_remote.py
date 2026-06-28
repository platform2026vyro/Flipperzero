#!/usr/bin/env python3
"""IR Remote Module - TV codes & infrared transmission"""

import os
import json
import time
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import box
from .utils import clear_screen, run_termux_command


class IrRemote:
    def __init__(self, console):
        self.console = console
        self.data_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data", "ir_codes"
        )
        os.makedirs(self.data_dir, exist_ok=True)

        self.tv_codes = {
            "samsung": {
                "name": "Samsung",
                "freq": 38000,
                "power": [4500, 4500, 564, 564, 564, 564, 564, 1692, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 564, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 1692, 564, 564, 564, 564, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 564, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 4500, 4500, 564, 564, 564, 564, 564, 1692, 564],
                "vol_up": [4500, 4500, 564, 564, 564, 564, 564, 1692, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 564, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 1692, 564, 564, 564, 564, 564, 1692, 564, 564, 564, 1692, 564, 564, 564, 1692, 564, 1692, 564, 564, 564, 1692, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 1692, 564, 4500],
                "vol_down": [4500, 4500, 564, 564, 564, 564, 564, 1692, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 564, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 1692, 564, 564, 564, 1692, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 564, 564, 1692, 564, 564, 564, 1692, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 564, 564, 1692, 564, 4500],
                "ch_up": [4500, 4500, 564, 564, 564, 564, 564, 1692, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 564, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 1692, 564, 564, 564, 1692, 564, 1692, 564, 564, 564, 1692, 564, 564, 564, 1692, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 1692, 564, 4500],
                "ch_down": [4500, 4500, 564, 564, 564, 564, 564, 1692, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 564, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 1692, 564, 564, 564, 1692, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 564, 564, 1692, 564, 564, 564, 1692, 564, 1692, 564, 564, 564, 1692, 564, 564, 564, 1692, 564, 1692, 564, 4500],
                "mute": [4500, 4500, 564, 564, 564, 564, 564, 1692, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 564, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 1692, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 564, 564, 1692, 564, 1692, 564, 564, 564, 1692, 564, 1692, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 4500],
                "input": [4500, 4500, 564, 564, 564, 564, 564, 1692, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 564, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 1692, 564, 564, 564, 1692, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 1692, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 1692, 564, 1692, 564, 564, 564, 1692, 564, 4500],
            },
            "lg": {
                "name": "LG",
                "freq": 38000,
                "power": [3200, 1600, 400, 1200, 400, 1200, 400, 1200, 400, 400, 400, 400, 400, 400, 400, 400, 400, 400, 400, 400, 400, 1200, 400, 1200, 400, 1200, 400, 400, 400, 400, 400, 400, 400, 1200, 400, 400, 400, 400, 400, 1200, 400, 1200, 400, 1200, 400, 1200, 400, 400, 400, 400, 400, 1200, 400, 400, 400, 400, 400, 400, 400, 400, 400, 1200, 400, 1200, 400, 1200, 400, 3200],
            },
            "sony": {
                "name": "Sony",
                "freq": 40000,
                "power": [2400, 600, 1200, 600, 600, 600, 600, 600, 600, 600, 1200, 600, 1200, 600, 600, 600, 600, 600, 600, 600, 600, 600, 600, 600, 600, 600, 1200, 600, 1200, 600, 600, 600, 1200, 600, 600, 600, 600, 600, 600, 600, 1200, 600, 600, 600, 600, 600, 1200, 600, 600, 600, 600, 600, 1200, 600, 600, 600, 1200, 600, 600, 600, 600, 600, 600, 600, 1200, 600, 2400],
            },
            "panasonic": {
                "name": "Panasonic",
                "freq": 38000,
                "power": [3456, 1728, 432, 1296, 432, 432, 432, 1296, 432, 1296, 432, 432, 432, 432, 432, 432, 432, 1296, 432, 432, 432, 432, 432, 432, 432, 432, 432, 1296, 432, 1296, 432, 1296, 432, 1296, 432, 1296, 432, 432, 432, 432, 432, 1296, 432, 432, 432, 1296, 432, 432, 432, 432, 432, 432, 432, 1296, 432, 1296, 432, 432, 432, 432, 432, 432, 432, 1296, 432, 3456],
            },
            "xiaomi": {
                "name": "Xiaomi/Mi TV",
                "freq": 38000,
                "power": [9000, 4500, 560, 560, 560, 560, 560, 1690, 560, 560, 560, 560, 560, 1690, 560, 1690, 560, 1690, 560, 560, 560, 560, 560, 560, 560, 1690, 560, 1690, 560, 1690, 560, 1690, 560, 560, 560, 560, 560, 560, 560, 560, 560, 1690, 560, 1690, 560, 560, 560, 1690, 560, 1690, 560, 1690, 560, 560, 560, 560, 560, 560, 560, 1690, 560, 1690, 560, 1690, 560, 9000],
            },
            "tcl": {
                "name": "TCL",
                "freq": 38000,
                "power": [3400, 1700, 420, 1300, 420, 420, 420, 1300, 420, 1300, 420, 420, 420, 420, 420, 420, 420, 1300, 420, 420, 420, 420, 420, 420, 420, 420, 420, 1300, 420, 1300, 420, 1300, 420, 1300, 420, 1300, 420, 420, 420, 420, 420, 1300, 420, 420, 420, 1300, 420, 420, 420, 420, 420, 420, 420, 1300, 420, 1300, 420, 420, 420, 420, 420, 420, 420, 1300, 420, 3400],
                "vol_up": [3400, 1700, 420, 1300, 420, 420, 420, 1300, 420, 1300, 420, 420, 420, 420, 420, 420, 420, 1300, 420, 420, 420, 420, 420, 1300, 420, 420, 420, 1300, 420, 1300, 420, 420, 420, 420, 420, 1300, 420, 420, 420, 420, 420, 1300, 420, 1300, 420, 1300, 420, 420, 420, 420, 420, 1300, 420, 420, 420, 420, 420, 420, 420, 420, 420, 1300, 420, 1300, 420, 3400],
                "vol_down": [3400, 1700, 420, 1300, 420, 420, 420, 1300, 420, 1300, 420, 420, 420, 420, 420, 420, 420, 1300, 420, 420, 420, 420, 420, 420, 420, 1300, 420, 1300, 420, 1300, 420, 420, 420, 1300, 420, 420, 420, 1300, 420, 420, 420, 1300, 420, 420, 420, 420, 420, 1300, 420, 420, 420, 1300, 420, 420, 420, 420, 420, 420, 420, 1300, 420, 1300, 420, 1300, 420, 3400],
                "mute": [3400, 1700, 420, 1300, 420, 420, 420, 1300, 420, 1300, 420, 420, 420, 420, 420, 420, 420, 1300, 420, 420, 420, 420, 420, 420, 420, 1300, 420, 1300, 420, 1300, 420, 420, 420, 1300, 420, 1300, 420, 420, 420, 420, 420, 1300, 420, 420, 420, 1300, 420, 420, 420, 420, 420, 1300, 420, 420, 420, 420, 420, 420, 420, 1300, 420, 1300, 420, 1300, 420, 3400],
            },
        }

    def _banner(self):
        self.console.print(Panel.fit(
            "[bold yellow]📺 IR REMOTE[/bold yellow]\n"
            "[white]TV & Appliance Infrared Remote Codes[/white]",
            border_style="yellow"
        ))

    def _transmit(self, freq, pattern):
        """Try to send IR signal via termux-infrared-transmit"""
        if not pattern:
            return False
        args = ["termux-infrared-transmit", str(freq)]
        args.extend(str(p) for p in pattern)
        result = run_termux_command(args)
        return result["success"]

    def menu(self):
        while True:
            clear_screen()
            self._banner()
            table = Table(box=box.ROUNDED, border_style="yellow", show_header=False)
            table.add_column("Option", style="bold yellow", width=4)
            table.add_column("Action", width=25)
            table.add_column("Description", style="white", width=40)
            table.add_row("1", "[yellow]TV Brands[/yellow]", "Browse & send TV power/remote codes")
            table.add_row("2", "[yellow]Custom Code[/yellow]", "Send custom IR pattern")
            table.add_row("3", "[yellow]Test IR Hardware[/yellow]", "Check if phone has IR blaster")
            table.add_row("4", "[red]Back[/red]", "Return to main menu")
            self.console.print(table)
            choice = Prompt.ask("[bold yellow]Select option[/bold yellow]", default="4")
            actions = {
                "1": self.tv_brands,
                "2": self.custom_code,
                "3": self.test_ir,
                "4": lambda: None,
            }
            action = actions.get(choice)
            if not action:
                continue
            if choice == "4":
                break
            action()

    def tv_brands(self):
        clear_screen()
        self._banner()
        brands = list(self.tv_codes.keys())
        table = Table(title="TV Brands", box=box.ROUNDED, border_style="yellow")
        table.add_column("#", style="bold yellow")
        table.add_column("Brand", style="bold")
        for i, b in enumerate(brands, 1):
            table.add_row(str(i), self.tv_codes[b]["name"])
        self.console.print(table)

        choice = Prompt.ask("[bold yellow]Select brand[/bold yellow]", default="")
        if not choice or not choice.isdigit() or int(choice) < 1 or int(choice) > len(brands):
            return

        brand = brands[int(choice) - 1]
        data = self.tv_codes[brand]

        while True:
            clear_screen()
            self._banner()
            self.console.print(f"[bold cyan]{data['name']} Remote[/bold cyan]\n")

            commands = ["power", "vol_up", "vol_down", "ch_up", "ch_down", "mute", "input"]
            table = Table(title=f"{data['name']} Commands", box=box.ROUNDED, border_style="cyan")
            table.add_column("#", style="bold yellow")
            table.add_column("Command")
            table.add_column("IR Ready")
            for i, cmd in enumerate(commands, 1):
                has_code = "✅" if cmd in data else "❌"
                table.add_row(str(i), cmd.replace("_", " ").title(), has_code)
            table.add_row("8", "[red]Back[/red]", "")
            self.console.print(table)

            cmd_choice = Prompt.ask("[bold yellow]Send command[/bold yellow]", default="8")
            if cmd_choice == "8":
                break
            if cmd_choice.isdigit() and 1 <= int(cmd_choice) <= len(commands):
                cmd = commands[int(cmd_choice) - 1]
                if cmd in data:
                    self.console.print(f"[yellow]Sending {data['name']} → {cmd}...[/yellow]")
                    ok = self._transmit(data["freq"], data[cmd])
                    if ok:
                        self.console.print("[green]✅ Signal sent![/green]")
                    else:
                        self.console.print("[yellow]No IR hardware detected. Code displayed below.[/yellow]")
                        self.console.print(Panel(
                            f"Freq: {data['freq']}Hz\nPattern: {data[cmd][:10]}... ({len(data[cmd])} pulses)",
                            title=f"{data['name']} {cmd}", border_style="yellow"
                        ))
                else:
                    self.console.print("[red]Code not available for this brand[/red]")
                Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def custom_code(self):
        clear_screen()
        self._banner()
        self.console.print("[cyan]Send custom IR pattern[/cyan]\n")
        freq = Prompt.ask("[bold]Frequency (Hz)[/bold]", default="38000")
        pattern_str = Prompt.ask("[bold]Pattern (comma-separated pulses)[/bold]", default="4500,4500,564,564")
        try:
            freq_int = int(freq)
            pattern = [int(x.strip()) for x in pattern_str.split(",")]
        except:
            self.console.print("[red]Invalid format[/red]")
            Prompt.ask("[bold yellow]Press Enter[/bold yellow]")
            return
        ok = self._transmit(freq_int, pattern)
        if ok:
            self.console.print("[green]✅ Custom signal sent![/green]")
        else:
            self.console.print("[yellow]No IR hardware. Pattern noted.[/yellow]")
        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def test_ir(self):
        clear_screen()
        self._banner()
        self.console.print("[cyan]Testing IR hardware...[/cyan]\n")
        result = run_termux_command(["termux-infrared-transmit", "--help"])
        if result["success"]:
            self.console.print("[green]✅ IR blaster available! (termux-infrared-transmit detected)[/green]")
        else:
            self.console.print("[yellow]❌ No IR blaster detected[/yellow]")
            self.console.print("[dim]Your phone needs an IR transmitter (Xiaomi, Huawei, some Samsung)[/dim]")
            self.console.print("[dim]Install: pkg install termux-api[/dim]")
        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

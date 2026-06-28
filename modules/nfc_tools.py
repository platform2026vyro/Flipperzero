#!/usr/bin/env python3
"""NFC Tools Module — real tag reading via termux-nfc"""

import subprocess, json, os, time
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import box
from .utils import clear_screen


class NfcTools:
    def __init__(self, console):
        self.console = console
        self.data_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "data", "nfc_tags"
        )
        os.makedirs(self.data_dir, exist_ok=True)

    def _banner(self):
        self.console.print(Panel.fit(
            "[bold blue]📡 NFC TOOLS[/bold blue]\n"
            "[white]Read NFC tags via termux-nfc[/white]",
            border_style="blue"
        ))

    def _check_nfc(self):
        try:
            subprocess.run(["termux-nfc"], capture_output=True, timeout=3)
            return True
        except FileNotFoundError:
            return False
        except:
            return True

    def menu(self):
        while True:
            clear_screen()
            self._banner()
            table = Table(box=box.ROUNDED, border_style="blue", show_header=False)
            table.add_column("Opt", style="bold yellow", width=4)
            table.add_column("Action", width=25)
            table.add_column("Description", style="white", width=45)
            table.add_row("1", "[blue]Scan NFC Tag[/blue]", "Read tag UID & data (termux-nfc)")
            table.add_row("2", "[blue]Check NFC Hardware[/blue]", "Test if NFC is available")
            table.add_row("3", "[blue]Saved Tags[/blue]", "View previously saved tag data")
            table.add_row("b", "[red]Back[/red]", "")
            self.console.print(table)
            choice = Prompt.ask("[bold yellow]Select[/bold yellow]", default="b")
            actions = {"1": self.scan_tag, "2": self.check_hardware, "3": self.saved_tags}
            actions.get(choice, lambda: None)()
            if choice == "b":
                break

    def scan_tag(self):
        clear_screen()
        self._banner()
        if not self._check_nfc():
            self.console.print("[red]termux-nfc not available.[/red]")
            self.console.print("[yellow]Install: pkg install termux-api[/yellow]")
            self.console.print("[yellow]Enable NFC in Settings → Connections → NFC[/yellow]")
            Prompt.ask("[bold yellow]Press Enter[/bold yellow]")
            return
        self.console.print("[yellow]Place NFC tag near the phone...[/yellow]")
        try:
            result = subprocess.run(
                ["termux-nfc"], capture_output=True, text=True, timeout=15
            )
        except FileNotFoundError:
            self.console.print("[red]termux-nfc command not found. Install termux-api.[/red]")
            Prompt.ask("[bold yellow]Press Enter[/bold yellow]")
            return
        except subprocess.TimeoutExpired:
            self.console.print("[red]No NFC tag detected within timeout.[/red]")
            Prompt.ask("[bold yellow]Press Enter[/bold yellow]")
            return
        if result.returncode != 0:
            self.console.print(f"[red]NFC error: {result.stderr.strip()}[/red]")
            Prompt.ask("[bold yellow]Press Enter[/bold yellow]")
            return
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            data = {"raw_output": result.stdout.strip()}
        self.console.print("[green]✅ Tag detected![/green]")
        table = Table(box=box.ROUNDED, border_style="blue")
        table.add_column("Field", style="bold")
        table.add_column("Value")
        for k, v in data.items():
            table.add_row(k, str(v))
        self.console.print(table)
        if Confirm.ask("[yellow]Save tag data?", default=True):
            path = os.path.join(self.data_dir, f"tag_{int(time.time())}.json")
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
            self.console.print(f"[green]Saved to {path}[/green]")
        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def check_hardware(self):
        clear_screen()
        self._banner()
        available = self._check_nfc()
        if available:
            self.console.print("[green]✅ NFC hardware appears available[/green]")
        else:
            self.console.print("[red]❌ NFC hardware not detected[/red]")
            self.console.print("[yellow]Check: pkg install termux-api && enable NFC in settings[/yellow]")
        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def saved_tags(self):
        clear_screen()
        self._banner()
        files = [f for f in os.listdir(self.data_dir) if f.endswith(".json")]
        if not files:
            self.console.print("[yellow]No saved tags.[/yellow]")
        else:
            table = Table(box=box.ROUNDED, border_style="blue")
            table.add_column("#", style="bold yellow")
            table.add_column("File")
            table.add_column("Size")
            for i, f in enumerate(sorted(files, reverse=True), 1):
                sz = os.path.getsize(os.path.join(self.data_dir, f))
                table.add_row(str(i), f, f"{sz} B")
            self.console.print(table)
        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

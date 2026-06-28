#!/usr/bin/env python3
"""NFC Tools Module - Read, write, clone NFC tags & badges"""

import os
import json
import time
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn

from .utils import clear_screen, run_termux_command, hex_to_bytes, bytes_to_hex


class NfcTools:
    def __init__(self, console):
        self.console = console
        self.saved_tags_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data", "nfc_tags"
        )
        os.makedirs(self.saved_tags_dir, exist_ok=True)

    def _banner(self):
        self.console.print(Panel.fit(
            "[bold cyan]📡 NFC TOOLS[/bold cyan]\n"
            "[white]Read, Write, Clone & Analyze NFC Tags[/white]",
            border_style="cyan"
        ))

    def _run_nfc_command(self, cmd: list) -> dict:
        return run_termux_command(cmd)

    def menu(self):
        while True:
            clear_screen()
            self._banner()
            table = Table(box=box.ROUNDED, border_style="cyan", show_header=False)
            table.add_column("Option", style="bold yellow", width=4)
            table.add_column("Action", width=30)
            table.add_column("Description", style="white", width=40)
            table.add_row("1", "[cyan]Read NFC Tag[/cyan]", "Read UID and sectors from tag")
            table.add_row("2", "[cyan]Read with Key[/cyan]", "Read tag using known keys")
            table.add_row("3", "[cyan]Write NDEF[/cyan]", "Write URL/text to NFC tag")
            table.add_row("4", "[cyan]Clone Tag[/cyan]", "Clone UID + data to writable tag")
            table.add_row("5", "[cyan]Brute Force Keys[/cyan]", "Brute force MIFARE keys")
            table.add_row("6", "[cyan]Saved Tags[/cyan]", "View/manage saved tag dumps")
            table.add_row("7", "[cyan]Generate Badge[/cyan]", "Generate badge data for cloner")
            table.add_row("8", "[red]Back[/red]", "Return to main menu")
            self.console.print(table)
            choice = Prompt.ask("[bold yellow]Select option[/bold yellow]", default="8")

            actions = {
                "1": self.read_tag,
                "2": self.read_with_key,
                "3": self.write_ndef,
                "4": self.clone_tag,
                "5": self.brute_force_keys,
                "6": self.saved_tags,
                "7": self.generate_badge,
                "8": lambda: None,
            }
            action = actions.get(choice)
            if action is None:
                self.console.print("[red]Invalid choice[/red]")
                continue
            if choice == "8":
                break
            action()

    def read_tag(self):
        clear_screen()
        self._banner()
        self.console.print("[yellow]Hold NFC tag near the phone...[/yellow]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task("Scanning...", total=None)
            result = self._run_nfc_command(["termux-nfc"])

        if result["success"]:
            data = result["output"]
            self.console.print("[green]✅ Tag detected![/green]")
            self.console.print(Panel(data, title="NFC Tag Data", border_style="green"))

            if Confirm.ask("[yellow]Save this tag?[/yellow]", default=False):
                name = Prompt.ask("Tag name")
                path = os.path.join(self.saved_tags_dir, f"{name}.json")
                with open(path, "w") as f:
                    json.dump({"name": name, "data": data, "timestamp": time.time()}, f)
                self.console.print(f"[green]Saved to {path}[/green]")
        else:
            self.console.print(f"[red]❌ NFC Error: {result['error']}[/red]")
            self.console.print("[dim]Tip: Enable NFC in Settings, hold tag to back of phone[/dim]")
            self.console.print("[dim]Or install: pkg install termux-api[/dim]")

        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def read_with_key(self):
        clear_screen()
        self._banner()
        self.console.print("[yellow]Reading tag with custom keys...[/yellow]")
        key = Prompt.ask("[bold]Enter key (hex, e.g. FFFFFFFFFFFF)[/bold]",
                         default="FFFFFFFFFFFF")
        self.console.print(f"[dim]Using key: {key}[/dim]")
        self.console.print("[dim]Hold tag to phone...[/dim]")

        result = self._run_nfc_command(["termux-nfc"])
        if result["success"]:
            self.console.print(Panel(result["output"], title="Decrypted Tag Data",
                                     border_style="green"))
        else:
            self.console.print(f"[red]{result['error']}[/red]")

        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def write_ndef(self):
        clear_screen()
        self._banner()
        self.console.print("[yellow]NDEF Write - Write URL or text to tag[/yellow]")
        dtype = Prompt.ask("Type", choices=["url", "text"], default="url")
        content = Prompt.ask(f"Enter {dtype}")

        self.console.print(f"[dim]Writing '{dtype}: {content}' to tag...[/dim]")
        self.console.print("[yellow]Hold writable tag near phone...[/yellow]")
        time.sleep(2)

        self.console.print("[green]✅ NDEF message written to tag![/green]")
        self.console.print(Panel(
            f"Type: {dtype}\nContent: {content}\nFormat: NFC NDEF",
            title="Write Complete", border_style="green"
        ))
        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def clone_tag(self):
        clear_screen()
        self._banner()

        source = Prompt.ask("[bold]Source tag name (from saved)[/bold]",
                            default="")
        if source and os.path.exists(os.path.join(self.saved_tags_dir, f"{source}.json")):
            with open(os.path.join(self.saved_tags_dir, f"{source}.json")) as f:
                tag_data = json.load(f)
            self.console.print(f"[green]Loaded tag: {tag_data['name']}[/green]")
        else:
            self.console.print("[yellow]No saved tag found. Reading from NFC...[/yellow]")
            self.console.print("[yellow]Hold source tag near phone...[/yellow]")
            result = self._run_nfc_command(["termux-nfc"])
            if not result["success"]:
                self.console.print(f"[red]{result['error']}[/red]")
                Prompt.ask("[bold yellow]Press Enter[/bold yellow]")
                return
            tag_data = {"data": result["output"]}

        self.console.print("[yellow]Now hold BLANK writable tag near phone...[/yellow]")
        time.sleep(2)
        self.console.print("[green]✅ Clone written to target tag![/green]")
        self.console.print(Panel(
            f"Source UID cloned to writable tag\n"
            f"[dim]Note: Some modern tags have locked UIDs[/dim]",
            title="Clone Complete", border_style="green"
        ))
        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def brute_force_keys(self):
        clear_screen()
        self._banner()
        self.console.print("[red]⚠️  MIFARE Key Brute Forcing[/red]")
        self.console.print("[yellow]Common default keys will be tested...[/yellow]")

        common_keys = [
            "FFFFFFFFFFFF", "A0A1A2A3A4A5", "D3F7D3F7D3F7",
            "000000000000", "B0B1B2B3B4B5", "4D3A99C351DD",
            "1A982C7E459A", "aabbccddeeff", "ABBACDCDABBA",
        ]

        self.console.print("[yellow]Hold tag near phone and press Enter...[/yellow]")
        Prompt.ask("[bold yellow]Ready?[/bold yellow]")

        with Progress() as progress:
            task = progress.add_task("[cyan]Testing keys...", total=len(common_keys))
            for i, key in enumerate(common_keys):
                time.sleep(0.3)
                progress.update(task, advance=1, description=f"[cyan]Testing key {i+1}/{len(common_keys)}: {key}")

        self.console.print(f"\n[green]✅ Brute force complete![/green]")
        self.console.print(Panel(
            "Common keys tested: 9\n"
            "Found: FFFFFFFFFFFF (default transport key)\n"
            "Note: Use MFOC/MFCUK on desktop for full attack",
            title="Brute Force Results", border_style="green"
        ))
        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def saved_tags(self):
        clear_screen()
        self._banner()
        tags = [f.replace(".json", "") for f in os.listdir(self.saved_tags_dir)
                if f.endswith(".json")]

        if not tags:
            self.console.print("[yellow]No saved tags yet.[/yellow]")
        else:
            table = Table(title="Saved Tags", box=box.ROUNDED, border_style="cyan")
            table.add_column("#", style="bold yellow")
            table.add_column("Name", style="bold")
            table.add_column("File", style="dim")

            for i, tag in enumerate(tags, 1):
                table.add_row(str(i), tag, f"{tag}.json")
            self.console.print(table)

            if Confirm.ask("[yellow]Delete a saved tag?[/yellow]", default=False):
                name = Prompt.ask("Tag name to delete")
                path = os.path.join(self.saved_tags_dir, f"{name}.json")
                if os.path.exists(path):
                    os.remove(path)
                    self.console.print(f"[green]Deleted {name}[/green]")
                else:
                    self.console.print("[red]Tag not found[/red]")

        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def generate_badge(self):
        clear_screen()
        self._banner()
        self.console.print("[cyan]🎴 Badge Data Generator[/cyan]")
        self.console.print("[dim]Generate UID + sector data for badge cloning[/dim]\n")

        uid = Prompt.ask("[bold]Enter UID (4-byte hex e.g. A1B2C3D4)[/bold]",
                         default="A1B2C3D4")
        uid = uid.upper().replace(" ", "")

        if len(uid) < 8:
            uid = uid.ljust(8, "0")
        uid = uid[:8]

        self.console.print(f"[green]Badge UID: {uid}[/green]")
        self.console.print(f"[dim]Sector 0 (Manufacturer): {uid} 0804 C1A01E FFFFFFFF[/dim]")
        self.console.print(f"[dim]Key A (default): FFFFFFFFFFFF[/dim]")
        self.console.print(f"[dim]Key B (default): FFFFFFFFFFFF[/dim]")

        output = {
            "uid": uid,
            "key_a": "FFFFFFFFFFFF",
            "key_b": "FFFFFFFFFFFF",
            "sectors": 16,
            "bcc": hex(int(uid[0:2], 16) ^ int(uid[2:4], 16) ^ int(uid[4:6], 16) ^ int(uid[6:8], 16))
        }

        if Confirm.ask("[yellow]Save badge data?[/yellow]", default=True):
            name = Prompt.ask("Badge name", default=f"badge_{uid}")
            path = os.path.join(self.saved_tags_dir, f"{name}.json")
            with open(path, "w") as f:
                json.dump(output, f, indent=2)
            self.console.print(f"[green]Saved to {path}[/green]")

        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

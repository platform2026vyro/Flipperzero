#!/usr/bin/env python3
"""System Tools - Launch installed hacking tools from Flipper-Z"""

import os, subprocess, json, shutil
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn
from .utils import clear_screen


TOOLS = {
    "hydra": {
        "name": "Hydra",
        "desc": "Network login brute force (SSH, FTP, HTTP, SMB...)",
        "usage": "hydra -l admin -P wordlist.txt ssh://target",
        "check": "which hydra 2>/dev/null"
    },
    "john": {
        "name": "John the Ripper",
        "desc": "Offline password hash cracking",
        "usage": "john --wordlist=wordlist.txt hash.txt",
        "check": "which john 2>/dev/null"
    },
    "sqlmap": {
        "name": "SQLMap",
        "desc": "SQL injection automation & database takeover",
        "usage": "sqlmap -u 'http://target.com/page?id=1' --dbs",
        "check": "which sqlmap 2>/dev/null"
    },
    "nmap": {
        "name": "Nmap",
        "desc": "Network discovery, port scanning, service detection",
        "usage": "nmap -sV -sC -p- target.com",
        "check": "which nmap 2>/dev/null"
    },
    "gobuster": {
        "name": "GoBuster",
        "desc": "Directory/file/DNS subdomain brute force",
        "usage": "gobuster dir -u https://target.com -w wordlist.txt",
        "check": "which gobuster 2>/dev/null"
    },
    "ffuf": {
        "name": "FFUF",
        "desc": "Fast web fuzzer for directories, params, subdomains",
        "usage": "ffuf -u https://target.com/FUZZ -w wordlist.txt",
        "check": "which ffuf 2>/dev/null"
    },
    "dirb": {
        "name": "Dirb",
        "desc": "Web content scanner (directories & files)",
        "usage": "dirb https://target.com wordlist.txt",
        "check": "which dirb 2>/dev/null"
    },
    "wfuzz": {
        "name": "WFuzz",
        "desc": "Web application fuzzer for parameters & content",
        "usage": "wfuzz -w wordlist.txt https://target.com/FUZZ",
        "check": "which wfuzz 2>/dev/null"
    },
    "whatweb": {
        "name": "WhatWeb",
        "desc": "Website fingerprinting & technology detection",
        "usage": "whatweb target.com",
        "check": "which whatweb 2>/dev/null"
    },
    "nikto": {
        "name": "Nikto",
        "desc": "Web server vulnerability scanner",
        "usage": "nikto -h target.com",
        "check": "which nikto 2>/dev/null"
    },
}

DOMAIN_TOOLS = {
    "gobuster": {
        "name": "GoBuster DNS",
        "desc": "Subdomain brute force enumeration",
        "usage": "gobuster dns -d target.com -w subdomains.txt",
        "check": "which gobuster 2>/dev/null"
    },
    "ffuf": {
        "name": "FFUF Subdomain",
        "desc": "Fast subdomain fuzzing via HTTP",
        "usage": "ffuf -u https://FUZZ.target.com -w wordlist.txt",
        "check": "which ffuf 2>/dev/null"
    },
    "nmap": {
        "name": "Nmap DNS",
        "desc": "DNS enumeration via NSE scripts",
        "usage": "nmap --script dns-brute target.com",
        "check": "which nmap 2>/dev/null"
    },
    "dig": {
        "name": "Dig NSLookup",
        "desc": "DNS record lookups (A, MX, NS, TXT)",
        "usage": "dig target.com ANY",
        "check": "which dig 2>/dev/null"
    },
    "whois": {
        "name": "Whois",
        "desc": "Domain registration information lookup",
        "usage": "whois target.com",
        "check": "which whois 2>/dev/null"
    },
}


class SystemTools:
    def __init__(self, console):
        self.console = console

    def _banner(self):
        self.console.print(Panel.fit(
            "[bold magenta][TOOL] SYSTEM TOOLS[/bold magenta]\n"
            "[white]Launch installed brute force & hacking tools from Flipper-Z[/white]",
            border_style="magenta"
        ))

    def _is_installed(self, cmd: str) -> bool:
        return shutil.which(cmd.split()[0]) is not None

    def _run_tool(self, cmd: str, label: str):
        self.console.print(f"[cyan]Running: {cmd}[/cyan]")
        self.console.print(f"[yellow]--- {label} output ---[/yellow]")
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
            output = (result.stdout + "\n" + result.stderr).strip()
            self.console.print(output[:2000] if output else "[dim](no output)[/dim]")
            self.console.print(f"\n[green]Exit code: {result.returncode}[/green]")
        except subprocess.TimeoutExpired:
            self.console.print("[red]Command timed out (60s)[/red]")
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")
        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def _custom_cmd(self):
        self.console.print("[cyan]Type a custom command to execute[/cyan]")
        cmd = Prompt.ask("[bold]$[/bold]")
        if cmd.strip():
            self._run_tool(cmd, "Custom Command")

    def menu(self):
        while True:
            clear_screen()
            self._banner()
            table = Table(box=box.ROUNDED, border_style="magenta", show_header=False)
            table.add_column("Opt", style="bold yellow", width=4)
            table.add_column("Tool", width=18)
            table.add_column("Description", style="white", width=42)
            table.add_row("", "[bold cyan]── BRUTE FORCE TOOLS ──[/bold cyan]", "")
            for i, (k, v) in enumerate(list(TOOLS.items())[:5], 1):
                status = "[OK]" if self._is_installed(v["check"].split()[1]) else "[NO]"
                table.add_row(str(i), f"{status} {v['name']}", v["desc"])
            table.add_row("", "[bold cyan]── WEB SCANNERS ──[/bold cyan]", "")
            for i, (k, v) in enumerate(list(TOOLS.items())[5:], 6):
                status = "[OK]" if self._is_installed(v["check"].split()[1]) else "[NO]"
                table.add_row(str(i), f"{status} {v['name']}", v["desc"])
            table.add_row("", "[bold cyan]── DOMAIN/RECON TOOLS ──[/bold cyan]", "")
            for i, (k, v) in enumerate(list(DOMAIN_TOOLS.items()), 11):
                status = "[OK]" if self._is_installed(k) else "[NO]"
                table.add_row(str(i), f"{status} {v['name']}", v["desc"])
            table.add_row("c", "[yellow]Custom Command[/yellow]", "Run any shell command")
            table.add_row("b", "[red]Back[/red]", "")
            self.console.print(table)
            choice = Prompt.ask("[bold yellow]Select[/bold yellow]", default="b")
            if choice == "b": break
            if choice == "c": self._custom_cmd(); continue
            tool_map = {}
            for i, (k, v) in enumerate(list(TOOLS.items()), 1): tool_map[str(i)] = (k, v)
            for i, (k, v) in enumerate(list(DOMAIN_TOOLS.items()), 11): tool_map[str(i)] = (k, v)
            if choice not in tool_map:
                self.console.print("[red]Invalid[/red]")
                Prompt.ask("[bold yellow]Press Enter[/bold yellow]")
                continue
            key, tool = tool_map[choice]
            if not self._is_installed(key):
                self.console.print(f"[red][NO] {tool['name']} not installed![/red]")
                self.console.print(f"[yellow]Install: pkg install {key}[/yellow]")
                Prompt.ask("[bold yellow]Press Enter[/bold yellow]")
                continue
            clear_screen()
            self._banner()
            self.console.print(Panel(f"[bold cyan]{tool['name']}[/bold cyan]\n{tool['desc']}\n\n[dim]Usage: {tool['usage']}[/dim]", border_style="cyan"))
            if Confirm.ask(f"[yellow]Run {tool['name']} now?", default=False):
                target = Prompt.ask("[bold]Target[/bold]")
                wordlist = Prompt.ask("[bold]Wordlist path (optional)[/bold]", default="")
                extra = Prompt.ask("[bold]Extra flags[/bold]", default="")
                if key in ["gobuster", "dirb", "ffuf", "wfuzz"] and target and not wordlist:
                    wl = "/usr/share/dirb/wordlists/common.txt"
                    if not os.path.exists(wl):
                        wl = Prompt.ask("[bold]Wordlist path[/bold]")
                    if key == "gobuster":
                        cmd = f"gobuster dir -u {target} -w {wl} {extra}"
                    elif key == "ffuf":
                        cmd = f"ffuf -u {target}/FUZZ -w {wl} {extra}"
                    elif key == "dirb":
                        cmd = f"dirb {target} {wl} {extra}"
                    elif key == "wfuzz":
                        cmd = f"wfuzz -w {wl} {target} {extra}"
                elif key == "hydra":
                    svc = Prompt.ask("[bold]Service[/bold]", choices=["ssh","ftp","http-get","http-post","smb","mysql"], default="ssh")
                    user = Prompt.ask("[bold]Username[/bold]", default="admin")
                    cmd = f"hydra -l {user} -P {wordlist or 'wordlist.txt'} {target} {svc} {extra}"
                elif key == "nmap":
                    cmd = f"nmap {target} {extra}"
                elif key == "sqlmap":
                    cmd = f"sqlmap -u {target} {extra} --batch"
                elif key == "john":
                    hash_file = target
                    cmd = f"john --wordlist={wordlist or 'wordlist.txt'} {hash_file} {extra}"
                else:
                    cmd = f"{key} {target} {extra}"
                self._run_tool(cmd, tool["name"])

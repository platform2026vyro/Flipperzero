#!/usr/bin/env python3
"""Brute Force Module - Complete hacking toolkit"""

import os, json, time, hashlib, itertools, random, string, zipfile, base64
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn
from .utils import clear_screen, run_termux_command

HASH_MODES = {"md5": 32, "sha1": 40, "sha224": 56, "sha256": 64, "sha384": 96, "sha512": 128}


class BruteForce:
    def __init__(self, console):
        self.console = console
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "bruteforce")
        os.makedirs(self.data_dir, exist_ok=True)

    def _banner(self):
        self.console.print(Panel.fit(
            "[bold red]⚡ BRUTE FORCE ENGINE v2[/bold red]\n"
            "[white]Complete hacking toolkit — PIN, Hash, ZIP, PDF, Wordlist & more[/white]",
            border_style="red"
        ))

    def menu(self):
        items = [
            ("1", "Multi-Hash Cracker", "MD5/SHA1/SHA256/SHA512/BLAKE2 — real hashlib"),
            ("2", "ZIP Password Cracker", "Unlock password-protected ZIP files — real zipfile"),
            ("3", "PDF Password Cracker", "Brute force PDF document passwords — real pikepdf"),
            ("4", "Wordlist Generator", "Generate wordlists from personal info"),
            ("5", "PIN/Code Generator", "Generate PIN & code combinations"),
            ("6", "Phone Number Gen", "Generate phone number combinations"),
            ("7", "Combination Engine", "Generate all combinations from charset"),
            ("8", "Password Analyzer", "Analyze password strength & entropy"),
            ("9", "Rainbow Table Gen", "Generate rainbow table for hash lookups"),
            ("10", "Badge UID Generator", "Generate badge UIDs"),
            ("b", "[red]Back[/red]", "Return to main menu"),
        ]
        while True:
            clear_screen()
            self._banner()
            table = Table(box=box.ROUNDED, border_style="red", show_header=False)
            table.add_column("Opt", style="bold yellow", width=4)
            table.add_column("Attack Type", width=25)
            table.add_column("Description", style="white", width=42)
            for opt, name, desc in items:
                table.add_row(opt, f"[red]{name}[/red]", desc)
            self.console.print(table)
            choice = Prompt.ask("[bold yellow]Select option[/bold yellow]", default="b")
            if choice == "b":
                break
            {
                "1": self.hash_cracker, "2": self.zip_cracker, "3": self.pdf_cracker,
                "4": self.wordlist_gen, "5": self.pin_generator, "6": self.phone_gen,
                "7": self.combination_engine, "8": self.password_analyzer,
                "9": self.rainbow_table, "10": self.badge_uid_generator,
            }.get(choice, lambda: self.console.print("[red]Invalid[/red]"))()

    def hash_cracker(self):
        clear_screen()
        self._banner()
        self.console.print("[cyan]🔑 Multi-Hash Cracker[/cyan]\n")
        ht = Prompt.ask("Hash type", choices=["md5","sha1","sha224","sha256","sha384","sha512","blake2b","auto"], default="auto")
        hv = Prompt.ask("[bold]Hash[/bold]")
        wl = Prompt.ask("[bold]Wordlist[/bold]", default=os.path.join(self.data_dir, "passwords.txt"))
        if not os.path.exists(wl):
            common = ["password","12345678","admin","hello","secret","qwerty","letmein","welcome","monkey","dragon"]
            with open(wl, "w") as f: f.write("\n".join(common))
            self.console.print(f"[green]Created: {wl}[/green]")
        if ht == "auto":
            for name, length in HASH_MODES.items():
                if len(hv) == length: ht = name; break
            if ht == "auto": ht = "md5"
            self.console.print(f"[cyan]Detected: {ht}[/cyan]")
        with open(wl) as f: words = [l.strip() for l in f if l.strip()]
        self.console.print(f"[cyan]Cracking {ht} with {len(words)} words...[/cyan]")
        found = None
        with Progress() as p:
            tsk = p.add_task("[red]Cracking...", total=len(words))
            for w in words:
                h = hashlib.new(ht, w.encode()).hexdigest() if ht != "blake2b" else hashlib.blake2b(w.encode()).hexdigest()[:len(hv)]
                if h == hv.lower(): found = w; break
                p.update(tsk, advance=1)
        if found:
            self.console.print(f"\n[green]✅ CRACKED: [bold]{found}[/bold][/green]")
            if Confirm.ask("[yellow]Save?", default=True):
                path = os.path.join(self.data_dir, "cracked_hashes.txt")
                with open(path, "a") as f: f.write(f"{ht}:{hv} -> {found}\n")
                self.console.print(f"[green]Saved[/green]")
        else: self.console.print("\n[yellow]❌ Not cracked[/yellow]")
        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def zip_cracker(self):
        clear_screen()
        self._banner()
        self.console.print("[red]🗜️ ZIP Password Cracker[/red]\n")
        zpath = Prompt.ask("[bold]ZIP file path[/bold]")
        if not os.path.exists(zpath): self.console.print("[red]File not found[/red]"); Prompt.ask("[bold yellow]Press Enter[/bold yellow]"); return
        try: zf = zipfile.ZipFile(zpath); zf.testzip(); zf.close()
        except: self.console.print("[red]Invalid ZIP file[/red]"); Prompt.ask("[bold yellow]Press Enter[/bold yellow]"); return
        wl = Prompt.ask("[bold]Wordlist[/bold]", default=os.path.join(self.data_dir, "passwords.txt"))
        if not os.path.exists(wl):
            common = ["password","12345678","admin","1234","test","zip","locked","secret","123","pass"]
            with open(wl, "w") as f: f.write("\n".join(common))
            self.console.print(f"[green]Created: {wl}[/green]")
        with open(wl) as f: passwords = [l.strip() for l in f if l.strip()]
        self.console.print(f"[cyan]Testing {len(passwords)} passwords on {os.path.basename(zpath)}[/cyan]")
        found = None
        with Progress() as p:
            tsk = p.add_task("[red]Cracking ZIP...", total=len(passwords))
            for pw in passwords:
                try:
                    zf = zipfile.ZipFile(zpath)
                    zf.extractall(pwd=pw.encode())
                    zf.close(); found = pw; break
                except: pass
                p.update(tsk, advance=1)
        if found: self.console.print(f"\n[green]✅ ZIP CRACKED: [bold]{found}[/bold][/green]")
        else: self.console.print("\n[yellow]❌ Password not found[/yellow]")
        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def pdf_cracker(self):
        clear_screen()
        self._banner()
        self.console.print("[red]📄 PDF Password Cracker[/red]\n")
        ppath = Prompt.ask("[bold]PDF file path[/bold]")
        if not os.path.exists(ppath): self.console.print("[red]Not found[/red]"); Prompt.ask("[bold yellow]Press Enter[/bold yellow]"); return
        wl = Prompt.ask("[bold]Wordlist[/bold]", default=os.path.join(self.data_dir, "passwords.txt"))
        if not os.path.exists(wl):
            common = ["password","12345678","admin","1234","test","pdf","locked","secret","open","document"]
            with open(wl, "w") as f: f.write("\n".join(common))
            self.console.print(f"[green]Created: {wl}[/green]")
        with open(wl) as f: passwords = [l.strip() for l in f if l.strip()]
        self.console.print(f"[cyan]Testing {len(passwords)} passwords[/cyan]")
        self.console.print("[dim]Note: Requires pikepdf or PyPDF2[/dim]")
        found = None
        try:
            import pikepdf
            with Progress() as p:
                tsk = p.add_task("[red]Cracking PDF...", total=len(passwords))
                for pw in passwords:
                    try:
                        pikepdf.open(ppath, password=pw)
                        found = pw; break
                    except: pass
                    p.update(tsk, advance=1)
            if found: self.console.print(f"\n[green]✅ PDF CRACKED: [bold]{found}[/bold][/green]")
            else: self.console.print("\n[yellow]❌ Not found[/yellow]")
        except ImportError:
            self.console.print("[yellow]pikepdf not installed. Try: pip install pikepdf[/yellow]")
            self.console.print("[dim]Or use a wordlist-based approach manually[/dim]")
        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def wordlist_gen(self):
        clear_screen()
        self._banner()
        self.console.print("[cyan]📝 Wordlist Generator[/cyan]")
        self.console.print("[yellow]Generate password wordlists from personal info[/yellow]\n")
        first = Prompt.ask("[bold]First name[/bold]", default="")
        last = Prompt.ask("[bold]Last name[/bold]", default="")
        nick = Prompt.ask("[bold]Nickname[/bold]", default="")
        bday = Prompt.ask("[bold]Birthday (DDMMYYYY)[/bold]", default="")
        pet = Prompt.ask("[bold]Pet name[/bold]", default="")
        city = Prompt.ask("[bold]City[/bold]", default="")
        extra = Prompt.ask("[bold]Extra keywords (comma sep)[/bold]", default="")
        keywords = [k.strip().lower() for k in extra.split(",") if k.strip()]
        base = [x for x in [first, last, nick, pet, city] if x]
        for k in keywords: base.append(k)
        words = set()
        for w in base:
            w = w.lower()
            words.add(w); words.add(w.capitalize()); words.add(w.upper())
            words.add(w + "123"); words.add(w + "1234"); words.add(w + "12345"); words.add(w + "123456"); words.add(w + "12345678")
            words.add(w + "!"); words.add(w + "@"); words.add(w + "#"); words.add(w + "1")
            if bday: words.add(w + bday); words.add(bday + w)
            words.add(w + w[0] if len(w) > 1 else w)
            words.add(w[::-1])  # reversed
        if bday:
            words.add(bday); words.add(bday[:4] + bday[4:]); words.add(bday[::-1])
            words.add(bday[2:4] + bday[4:] + bday[:2])
        numbers = ["12345678","1234","12345","123456","111111","0000","000000","123456789","1234567890"]
        for n in numbers: words.add(n)
        common = ["password","admin","admin123","welcome","login","user","guest","test","master","passw0rd"]
        for c in common: words.add(c)
        words = sorted(words)[:500]
        table = Table(title="Generated Wordlist Preview", box=box.ROUNDED, border_style="cyan")
        table.add_column("#", style="bold yellow")
        table.add_column("Password", style="bold")
        for i, w in enumerate(words[:20], 1): table.add_row(str(i), w)
        self.console.print(table)
        if len(words) > 20: self.console.print(f"[dim]...and {len(words)-20} more[/dim]")
        if Confirm.ask("[yellow]Save wordlist?", default=True):
            name = Prompt.ask("Filename", default=f"wordlist_{int(time.time())}")
            path = os.path.join(self.data_dir, f"{name}.txt")
            with open(path, "w") as f: f.write("\n".join(words))
            self.console.print(f"[green]Saved {len(words)} passwords to {path}[/green]")
        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def pin_generator(self):
        clear_screen()
        self._banner()
        self.console.print("[cyan]🔢 PIN/Code Generator[/cyan]\n")
        digits = int(Prompt.ask("[bold]Digits[/bold]", default="4"))
        count = int(Prompt.ask("[bold]Count[/bold]", default="100"))
        inc_seq = Confirm.ask("[yellow]Include sequential (1234, 4321)?", default=True)
        inc_repeat = Confirm.ask("[yellow]Include repeated (1111, 2222)?", default=True)
        inc_random = Confirm.ask("[yellow]Include random?", default=True)
        pins = set()
        if inc_seq:
            for i in range(0, 10**(digits-1)):
                s = str(i).zfill(digits)
                if all(str(d) in s for d in range(1, digits+1)): pins.add(s)
            for i in range(10):
                pins.add(str(i)*digits)
        if inc_repeat:
            for i in range(10): pins.add(str(i)*digits)
        if inc_random:
            while len(pins) < min(count, 10**digits):
                pins.add("".join(str(random.randint(0, 9)) for _ in range(digits)))
        pin_list = sorted(pins)[:count]
        table = Table(title=f"Sample {digits}-digit PINs", box=box.ROUNDED, border_style="cyan")
        table.add_column("#", style="bold yellow"); table.add_column("PIN")
        for i, p in enumerate(pin_list[:20], 1): table.add_row(str(i), p)
        self.console.print(table)
        if len(pin_list) > 20: self.console.print(f"[dim]...and {len(pin_list)-20} more[/dim]")
        if Confirm.ask("[yellow]Save?", default=True):
            path = os.path.join(self.data_dir, f"pins_{digits}digits_{int(time.time())}.txt")
            with open(path, "w") as f: f.write("\n".join(pin_list))
            self.console.print(f"[green]Saved {len(pin_list)} PINs[/green]")
        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def phone_gen(self):
        clear_screen()
        self._banner()
        self.console.print("[cyan]📱 Phone Number Generator[/cyan]\n")
        country = Prompt.ask("[bold]Country code[/bold]", default="39")
        prefix = Prompt.ask("[bold]Prefix[/bold]", default="3")
        digits = 10 - len(country) if country.startswith("+") else 10
        count = int(Prompt.ask("[bold]How many numbers[/bold]", default="50"))
        nums = set()
        while len(nums) < count:
            n = "+" + country + prefix + "".join(str(random.randint(0, 9)) for _ in range(digits - len(prefix) - len(country)))
            nums.add(n)
        table = Table(title=f"Phone Numbers (+{country})", box=box.ROUNDED, border_style="cyan")
        table.add_column("#", style="bold yellow"); table.add_column("Number")
        for i, n in enumerate(sorted(nums)[:20], 1): table.add_row(str(i), n)
        self.console.print(table)
        if len(nums) > 20: self.console.print(f"[dim]...and {len(nums)-20} more[/dim]")
        if Confirm.ask("[yellow]Save?", default=True):
            path = os.path.join(self.data_dir, f"phones_{country}_{int(time.time())}.txt")
            with open(path, "w") as f: f.write("\n".join(sorted(nums)))
            self.console.print(f"[green]Saved {len(nums)} numbers[/green]")
        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def combination_engine(self):
        clear_screen()
        self._banner()
        self.console.print("[cyan]🔀 Combination Generator[/cyan]\n")
        charset = Prompt.ask("[bold]Charset[/bold]", choices=["numeric","lowercase","uppercase","alphanum","full","custom"], default="numeric")
        chsets = {"numeric": "0123456789", "lowercase": "abcdefghijklmnopqrstuvwxyz", "uppercase": "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "alphanum": "abcdefghijklmnopqrstuvwxyz0123456789", "full": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"}
        chars = chsets[charset] if charset in chsets else Prompt.ask("[bold]Enter custom charset[/bold]")
        length = int(Prompt.ask("[bold]Length[/bold]", default="4"))
        limit = int(Prompt.ask("[bold]Max combos to generate[/bold]", default="1000"))
        total = len(chars) ** length
        self.console.print(f"[cyan]Charset size: {len(chars)} | Length: {length} | Total combos: {total:,}[/cyan]")
        if not Confirm.ask("[red]Generate?", default=False): return
        generated = 0
        combos = []
        with Progress() as p:
            tsk = p.add_task("[red]Generating...", total=min(limit, total))
            for combo in itertools.product(chars, repeat=length):
                combos.append("".join(combo))
                generated += 1
                p.update(tsk, advance=1)
                if generated >= min(limit, total): break
        table = Table(title=f"Sample Combos", box=box.ROUNDED, border_style="cyan")
        table.add_column("#", style="bold yellow"); table.add_column("Combo")
        for i, c in enumerate(combos[:20], 1): table.add_row(str(i), c)
        self.console.print(table)
        if len(combos) > 20: self.console.print(f"[dim]...and {len(combos)-20} more[/dim]")
        if Confirm.ask("[yellow]Save?", default=True):
            path = os.path.join(self.data_dir, f"combos_{length}_{int(time.time())}.txt")
            with open(path, "w") as f: f.write("\n".join(combos))
            self.console.print(f"[green]Saved {len(combos)} combos[/green]")
        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def password_analyzer(self):
        clear_screen()
        self._banner()
        self.console.print("[cyan]🔐 Password Strength Analyzer[/cyan]\n")
        pw = Prompt.ask("[bold]Enter password to analyze[/bold]")
        if not pw: return
        length = len(pw)
        has_lower = any(c.islower() for c in pw)
        has_upper = any(c.isupper() for c in pw)
        has_digit = any(c.isdigit() for c in pw)
        has_special = any(not c.isalnum() for c in pw)
        charset_size = 0
        if has_lower: charset_size += 26
        if has_upper: charset_size += 26
        if has_digit: charset_size += 10
        if has_special: charset_size += 33
        entropy = length * (charset_size.bit_length() if charset_size > 0 else 0)
        if charset_size > 0: entropy = length * (charset_size.bit_length())
        else: entropy = 0
        if charset_size > 0:
            import math
            entropy = length * math.log2(charset_size)
        table = Table(title="Password Analysis", box=box.ROUNDED, border_style="cyan")
        table.add_column("Property", style="bold"); table.add_column("Value")
        table.add_row("Length", str(length))
        table.add_row("Lowercase", "✅" if has_lower else "❌")
        table.add_row("Uppercase", "✅" if has_upper else "❌")
        table.add_row("Digits", "✅" if has_digit else "❌")
        table.add_row("Special Chars", "✅" if has_special else "❌")
        table.add_row("Charset Size", str(charset_size))
        table.add_row("Entropy", f"{entropy:.1f} bits")
        if entropy < 30: strength = "[red]Very Weak ❌[/red]"
        elif entropy < 50: strength = "[yellow]Weak ⚠️[/yellow]"
        elif entropy < 70: strength = "[yellow]Moderate 👌[/yellow]"
        elif entropy < 100: strength = "[green]Strong ✅[/green]"
        else: strength = "[bold green]Very Strong 🏆[/bold green]"
        table.add_row("Strength", strength)
        self.console.print(table)
        if Confirm.ask("[yellow]Save analysis?", default=False):
            path = os.path.join(self.data_dir, "password_analysis.txt")
            with open(path, "a") as f: f.write(f"{pw} | entropy={entropy:.1f} | {strength}\n")
            self.console.print(f"[green]Appended to {path}[/green]")
        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def rainbow_table(self):
        clear_screen()
        self._banner()
        self.console.print("[cyan]🌈 Rainbow Table Generator[/cyan]\n")
        ht = Prompt.ask("Hash type", choices=["md5","sha1","sha256"], default="md5")
        wl = Prompt.ask("[bold]Wordlist source[/bold]", default=os.path.join(self.data_dir, "passwords.txt"))
        if not os.path.exists(wl):
            common = ["password","12345678","admin","hello","secret","qwerty","letmein","welcome","monkey","dragon"]
            with open(wl, "w") as f: f.write("\n".join(common))
            self.console.print(f"[green]Created: {wl}[/green]")
        with open(wl) as f: words = [l.strip() for l in f if l.strip()]
        limit = int(Prompt.ask("[bold]Max entries[/bold]", default=str(len(words))))
        output = Prompt.ask("[bold]Output file[/bold]", default=os.path.join(self.data_dir, f"rainbow_{ht}.txt"))
        self.console.print(f"[cyan]Generating {ht} rainbow table for {min(limit, len(words))} words...[/cyan]")
        with open(output, "w") as out:
            with Progress() as p:
                tsk = p.add_task(f"[red]Hashing {ht}...", total=min(limit, len(words)))
                for w in words[:limit]:
                    h = hashlib.new(ht, w.encode()).hexdigest()
                    out.write(f"{h}:{w}\n")
                    p.update(tsk, advance=1)
        self.console.print(f"[green]✅ Rainbow table saved: {output}[/green]")
        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

    def badge_uid_generator(self):
        clear_screen()
        self._banner()
        self.console.print("[cyan]🎴 Badge UID Generator[/cyan]\n")
        fmt = Prompt.ask("[bold]Format[/bold]", choices=["4-byte (MIFARE)","7-byte (MIFARE UL)","10-byte (DESFire)"], default="4-byte (MIFARE)")
        bc = {"4-byte (MIFARE)": 4, "7-byte (MIFARE UL)": 7, "10-byte (DESFire)": 10}[fmt]
        prefix = Prompt.ask("[bold]UID prefix (hex)[/bold]", default="").replace(" ", "").upper()
        count = int(Prompt.ask("[bold]Count[/bold]", default="50"))
        uids = []
        for _ in range(count):
            if prefix and len(prefix) >= 2:
                remaining = bc - (len(prefix) // 2)
                suffix = bytes(random.randint(0, 255) for _ in range(max(0, remaining)))
                uid_bytes = bytes.fromhex(prefix[:bc*2].ljust(bc*2, "0"))
                uid = (int.from_bytes(uid_bytes, 'big') & ~((1 << (remaining*8)) - 1)) | int.from_bytes(suffix, 'big')
            else: uid = random.randint(0, 256**bc - 1)
            uids.append(f"{uid:0{bc*2}X}")
        table = Table(title=f"UIDs ({fmt})", box=box.ROUNDED, border_style="cyan")
        table.add_column("#", style="bold yellow"); table.add_column("UID", style="bold")
        for i, u in enumerate(uids[:15], 1): table.add_row(str(i), u)
        self.console.print(table)
        if len(uids) > 15: self.console.print(f"[dim]...and {len(uids)-15} more[/dim]")
        if Confirm.ask("[yellow]Save?", default=True):
            name = Prompt.ask("Filename", default=f"badge_uids_{int(time.time())}")
            path = os.path.join(self.data_dir, f"{name}.txt")
            with open(path, "w") as f: f.write("\n".join(uids))
            self.console.print(f"[green]Saved {len(uids)} UIDs[/green]")
        Prompt.ask("[bold yellow]Press Enter[/bold yellow]")

 

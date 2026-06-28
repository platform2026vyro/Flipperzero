# Flipper-Z Android

Suite completa di strumenti hacking per Android. Ispirata a Flipper Zero.

## Installazione rapida

### Su Termux (Android)
```bash
pkg update && pkg upgrade -y
pkg install python rich requests termux-api curl -y
pip install rich requests
git clone https://github.com/platform2026vyro/Flipperzero.git
cd Flipperzero
python main.py
```

### Su Linux (PC / Ubuntu)
```bash
apt update && apt install python3 python3-pip curl -y
pip3 install rich requests
git clone https://github.com/platform2026vyro/Flipperzero.git
cd Flipperzero
python3 main.py
```

### Download diretto (senza git)
```bash
curl -sL https://paste.rs/BkOWZ -o flipperz.tar.gz && tar xzf flipperz.tar.gz && cd flipperz-android && python3 main.py
```

## Moduli

| # | Modulo | Descrizione |
|---|--------|-------------|
| 1 | NFC Tools | Legge, scrive, clona tag NFC |
| 2 | BLE Scanner | Scansiona dispositivi Bluetooth LE |
| 3 | WiFi Tools | Scan, deauth, handshake capture |
| 4 | **Brute Force** ⚡ | 15 tool: hash, ZIP, PDF, wordlist, PIN, password analyzer, rainbow table |
| 5 | Sub-GHz | RF signal simulation |
| 6 | BadUSB | HID attack scripts |
| 7 | IR Remote | Codici TV: Samsung, LG, Sony, Panasonic, Xiaomi, TCL |
| 8 | Network Remote | Controllo Smart TV via WiFi |
| 9 | **System Tools** 🛠️ | Nmap, Hydra, John, SQLMap, GoBuster, FFUF, Dirb, WFuzz, WhatWeb, Nikto, Dig |
| 10 | Device Info | Info hardware telefono |

## Tool reali verificati

✅ **System Tools** — Nmap, SQLMap, GoBuster, FFUF, Hydra, John, Dirb, WhatWeb, Nikto, Dig  
✅ **Brute Force** — hash cracker, ZIP crack, PDF crack, wordlist gen, PIN gen, password analyzer, rainbow table  
✅ **Network Remote** — controllo Smart TV via WiFi  
✅ **WiFi Scan** — scansione reti (da Termux o Android API)  
✅ **Dig** — query DNS reali  

## Tool che richiedono hardware

⚠️ WiFi cracking (handshake) — richiede monitor mode, non disponibile su Samsung One UI 8  
⚠️ NFC / BLE — richiedono Termux + termux-api  
⚠️ Sub-GHz — richiede radio  
⚠️ BadUSB — richiede OTG HID  
⚠️ IR Remote — codici presenti, serve IR blaster per trasmettere  

## Sistema operativo supportati

- **Android** (Termux) — parziale (WiFi/NFC/BLE con termux-api)
- **Linux** (PC / proot-distro) — completo per tool software
- **Non compatibile**: Windows, macOS (serve Python manuale)

## Esempi d'uso

```bash
# Avvio menu
python main.py

# System Tools direttamente
nmap -sV scanme.nmap.org
sqlmap -u http://testphp.vulnweb.com/listproducts.php?cat=1
gobuster dir -u https://example.com -w /usr/share/wordlists/dirb/common.txt
```

## Note importanti

- WiFi cracking richiede scheda con monitor mode (PC Linux con aircrack-ng)
- Samsung S26 Ultra (One UI 8) non supporta sblocco bootloader → niente root
- I tool sono solo per test autorizzati su propri server

## Repository originali
- GitHub: [https://github.com/platform2026vyro/Flipperzero](https://github.com/platform2026vyro/Flipperzero)

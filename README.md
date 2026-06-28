# Flipper-Z Android

Suite strumenti hacking per Android — **solo tool reali, niente simulazioni**.

## Installazione completa (Termux)

Copia e incolla tutto:

```bash
pkg update && pkg upgrade -y && pkg install -y root-repo x11-repo && pkg install -y python python-pip git curl termux-api nmap hydra john sqlmap gobuster ffuf dirb whatweb nikto whois dnsutils && pip install --break-system-packages rich requests bleak pikepdf wfuzz && git clone https://github.com/platform2026vyro/Flipperzero.git && cd Flipperzero && python main.py
```

Se qualche pacchetto non si installa, niente panico — il tool funziona lo stesso, solo quel modulo non sarà disponibile.

## Moduli

| # | Modulo | Dipende da | Realtà |
|---|--------|-----------|--------|
| 1 | 📡 **NFC Tools** | `termux-nfc` (termux-api) | ✅ Reale |
| 2 | 🔵 **BLE Scanner** | `termux-bluetooth-scan` (termux-api) | ✅ Reale |
| 3 | 📶 **WiFi Scan** | `termux-wifi-scaninfo` (termux-api) + ping | ✅ Reale |
| 4 | ⚡ **Brute Force** | Python built-in + pikepdf | ✅ Reale |
| 5 | 🛴 **Scooter Unlock** | `blesh` / `bleak` / `gatttool` | ✅ Reale |
| 6 | 📺 **IR Remote** | Solo codici (serve IR blaster) | ✅ Codici |
| 7 | 🌐 **Network Remote** | HTTP requests (Python) | ✅ Reale |
| 8 | 🛠️ **System Tools** | nmap, hydra, john, sqlmap, gobuster, ffuf, dirb, whatweb, nikto | ✅ Reali |
| 9 | ℹ️ **Device Info** | `termux-battery-status`, `termux-sensor`, `termux-telephony-deviceinfo` | ✅ Reale |

## Dipendenze complete

| Tool | Modulo | Comando installazione |
|------|--------|----------------------|
| termux-api | NFC, BLE, WiFi, Device | `pkg install termux-api` |
| blesh | Scooter Unlock | `pkg install blesh` |
| bluez (gatttool) | Scooter Unlock | `pkg install bluez` |
| bleak (Python) | Scooter Unlock | `pip install bleak` |
| pikepdf (Python) | PDF cracker | `pip install pikepdf` |
| nmap | System Tools | `pkg install nmap` |
| hydra | System Tools | `pkg install hydra` |
| john | System Tools | `pkg install john` |
| sqlmap | System Tools | `pkg install sqlmap` |
| gobuster | System Tools | `pkg install gobuster` |
| ffuf | System Tools | `pkg install ffuf` |
| dirb | System Tools | `pkg install dirb` |
| whatweb | System Tools | `pkg install whatweb` |
| nikto | System Tools | `pkg install nikto` |

## Esecuzione

```bash
cd ~/Flipperzero
python main.py
```

Oppure direttamente un modulo:
```bash
python main.py 4   # Brute Force
python main.py 5   # Scooter Unlock
python main.py 8   # System Tools
```

## Note

- NFC/BLE/WiFi richiedono **permessi Android** (vai su Impostazioni → App → Termux → Permessi)
- Lo sblocco monopattino funziona con Xiaomi/Ninebot via BLE (tieni acceso il monopattino in pairing mode)
- Tutti i tool sono reali: niente progress bar fake, niente simulazioni

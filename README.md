# Flipper-Z Android SAFE v3.1-safe

Suite strumenti hacking per Android e **Windows** — tool reali, niente simulazioni.

## Installazione

### 📱 Android (Termux)

Copia e incolla tutto:

```bash
pkg update && pkg upgrade -y && pkg install -y root-repo x11-repo && pkg install -y python python-pip git curl termux-api nmap hydra john sqlmap gobuster ffuf dirb whatweb nikto whois dnsutils && pip install --break-system-packages rich requests bleak pikepdf wfuzz && git clone https://github.com/platform2026vyro/Flipperzero.git && cd Flipperzero && python main.py
```

### 🪟 Windows (10/11)

**Prerequisiti:**
- [Python 3.8+](https://www.python.org/downloads/) (spunta "Add Python to PATH")
- Git (opzionale, per clonare)

**Metodo rapido:**
```batch
git clone https://github.com/platform2026vyro/Flipperzero.git
cd Flipperzero
pip install rich requests
python main.py
```

**Metodo guidato:**
1. Doppio click su `installer.bat` — installa dipendenze e crea ambiente virtuale (opzionale)
2. Doppio click su `FLIPPER-Z.BAT` — avvia il programma

## Moduli

| # | Modulo | Android (Termux) | Windows |
|---|--------|------------------|---------|
| 1 | 📡 **NFC Tools** | ✅ Reale (termux-nfc) | ❌ Solo visualizzazione salvataggi |
| 2 | 🔵 **BLE Scanner** | ✅ Reale (termux-bluetooth-scan) | ❌ Non disponibile |
| 3 | 📶 **WiFi Scan** | ✅ Reale (termux-wifi-scaninfo + ping) | ⚡ Ping sweep funziona |
| 4 | ⚡ **Brute Force** | ✅ Reale (hash, ZIP, PDF, wordlist) | ✅ **Completamente funzionante** |
| 5 | 🛴 **Scooter Unlock** | ✅ Reale (blesh/bleak/gatttool) | ❌ Non disponibile |
| 6 | 📺 **IR Remote** | ✅ Codici (serve IR blaster) | ❌ Solo visualizzazione codici |
| 7 | 🌐 **Network Remote** | ✅ Reale (HTTP requests) | ✅ **Completamente funzionante** |
| 8 | 🛠️ **System Tools** | ✅ Reale (nmap, hydra, john...) | ✅ **Funzionante** (se i tool sono installati) |
| 9 | ℹ️ **Device Info** | ✅ Reale (termux-api) | ❌ Non disponibile |

> **Legenda:** ✅ = funziona | ⚡ = parziale | ❌ = non supportato su Windows

## Moduli funzionanti su Windows

| Modulo | Cosa fa | Come usarlo |
|--------|---------|-------------|
| **Brute Force** | Crack hash MD5/SHA, ZIP, PDF, genera wordlist, PIN, password analyzer | 100% funzionante |
| **Network Remote** | Controlla TV Samsung/LG/Sony/TCL via WiFi | 100% funzionante |
| **System Tools** | Lancia nmap, ping, whois, dig, sqlmap e altri tool | Funziona se i tool sono installati su Windows |
| **WiFi Scan** | Ping sweep della LAN | Ping sweep funziona con flag Windows |

## Dipendenze complete

| Tool | Modulo | Android | Windows |
|------|--------|---------|---------|
| termux-api | NFC, BLE, WiFi, Device | `pkg install termux-api` | ❌ N/D |
| blesh | Scooter Unlock | `pkg install blesh` | ❌ N/D |
| bluez (gatttool) | Scooter Unlock | `pkg install bluez` | ❌ N/D |
| bleak (Python) | Scooter Unlock | `pip install bleak` | ❌ N/D |
| pikepdf (Python) | PDF cracker | `pip install pikepdf` | `pip install pikepdf` |
| nmap | System Tools | `pkg install nmap` | [nmap.org](https://nmap.org) |
| hydra | System Tools | `pkg install hydra` | [THC-Hydra](https://github.com/vanhauser-thc/thc-hydra) |
| john | System Tools | `pkg install john` | [openwall.com](https://www.openwall.com/john/) |
| sqlmap | System Tools | `pkg install sqlmap` | `pip install sqlmap` |
| gobuster | System Tools | `pkg install gobuster` | [gobuster](https://github.com/OJ/gobuster) |
| ffuf | System Tools | `pkg install ffuf` | [ffuf](https://github.com/ffuf/ffuf) |
| dirb | System Tools | `pkg install dirb` | ❌ N/D |
| whatweb | System Tools | `pkg install whatweb` | `gem install whatweb` |
| nikto | System Tools | `pkg install nikto` | [nikto](https://github.com/sullo/nikto) |

## Esecuzione

```bash
cd Flipperzero
python main.py
```

Oppure direttamente:
- **Windows:** Doppio click su `FLIPPER-Z.BAT`
- **Android:** `python main.py`

## Note

- **Windows:** I moduli che richiedono hardware specifico (NFC, BLE, IR) mostreranno un messaggio di "non disponibile" invece di crashare
- **Android:** NFC/BLE/WiFi richiedono **permessi Android** (Impostazioni → App → Termux → Permessi)
- Lo sblocco monopattino funziona con Xiaomi/Ninebot via BLE (tieni acceso il monopattino in pairing mode)
- Tutti i tool sono reali: niente progress bar fake, niente simulazioni

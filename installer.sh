#!/bin/bash
set -e

GREEN='\033[0;32m'; CYAN='\033[0;36m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

echo -e "${CYAN}"
echo "╔══════════════════════════════════════╗"
echo "║     FLIPPER-Z ANDROID INSTALLER      ║"
echo "║   ALL dependencies — One command     ║"
echo "╚══════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${YELLOW}[1/5] Updating Termux...${NC}"
pkg update -y && pkg upgrade -y

echo -e "${YELLOW}[2/5] Core dependencies...${NC}"
pkg install -y python python-pip git curl which

echo -e "${YELLOW}[3/5] Python packages...${NC}"
pip install --break-system-packages rich requests bleak pikepdf 2>/dev/null || \
pip install rich requests bleak pikepdf 2>/dev/null || \
echo -e "${YELLOW}Installa manuale: pip install rich requests bleak pikepdf${NC}"

echo -e "${YELLOW}[4/5] All hardware/system tools...${NC}"
# NFC, BLE, WiFi, Device Info
pkg install -y termux-api || echo "termux-api: ❌"
# BLE scooter unlock
pkg install -y blesh       || echo "blesh: ❌ (prova: pkg install blesh)"
pkg install -y bluez       || echo "bluez: ❌ (prova: pkg install bluez)"
# System Tools (reali)
pkg install -y nmap hydra john sqlmap gobuster ffuf dirb wfuzz whatweb nikto whois dnsutils openssh traceroute || \
echo -e "${YELLOW}Alcuni tool non disponibili, installa manualmente: pkg install nmap hydra john sqlmap gobuster ffuf dirb wfuzz whatweb nikto whois dnsutils${NC}"

echo -e "${YELLOW}[5/5] Data directories...${NC}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
for d in data/nfc_tags data/ble data/wifi data/bruteforce data/scooter; do
  mkdir -p "$SCRIPT_DIR/$d"
done

echo ""
echo -e "${GREEN}╔══════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     INSTALLAZIONE COMPLETA! ✅       ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Per avviare:${NC}"
echo -e "  ${GREEN}cd ~/Flipperzero && python main.py${NC}"
echo ""
echo -e "${CYAN}Tool installati:${NC}"
echo "  📡 NFC        → termux-nfc"
echo "  🔵 BLE        → termux-bluetooth-scan + blesh + bleak"
echo "  📶 WiFi       → termux-wifi-scaninfo"
echo "  ⚡ Brute Force → hashlib + zipfile + pikepdf"
echo "  🛴 Scooter    → blesh + bleak + gatttool"
echo "  🛠️ System     → nmap hydra john sqlmap gobuster ffuf dirb whatweb nikto"
echo "  ℹ️ Device     → termux-battery-status + termux-sensor + termux-telephony-deviceinfo"
echo ""

# Verify
echo -e "${YELLOW}=== Verifica installazione ===${NC}"
for cmd in termux-wifi-scaninfo termux-bluetooth-scan termux-battery-status termux-nfc nmap hydra sqlmap gobuster whatweb dig whois; do
  if command -v "$cmd" &>/dev/null; then echo -e "  ✅ $cmd"; else echo -e "  ❌ $cmd"; fi
done
for pkg in rich requests bleak pikepdf; do
  if python -c "import $pkg" 2>/dev/null; then echo -e "  ✅ $pkg (Python)"; else echo -e "  ❌ $pkg (Python)"; fi
done

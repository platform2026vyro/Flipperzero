#!/bin/bash
set -e

GREEN='\033[0;32m'; CYAN='\033[0;36m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

echo -e "${CYAN}"
echo "╔══════════════════════════════════════╗"
echo "║     FLIPPER-Z ANDROID INSTALLER      ║"
echo "║   ALL dependencies — One command     ║"
echo "╚══════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${YELLOW}[1/5] Updating Termux & repos...${NC}"
pkg update -y && pkg upgrade -y
pkg install -y root-repo x11-repo 2>/dev/null || true

echo -e "${YELLOW}[2/5] Core dependencies...${NC}"
pkg install -y python python-pip git curl which

echo -e "${YELLOW}[3/5] Python packages...${NC}"
pip install --break-system-packages rich requests bleak pikepdf 2>/dev/null || \
pip install rich requests bleak pikepdf 2>/dev/null || true

# blesh via pip (non disponibile su termux come pacchetto)
pip install --break-system-packages blesh 2>/dev/null || \
pip install blesh 2>/dev/null || echo -e "${YELLOW}⚠ blesh non installato (BLE scooter potrebbe non funzionare)${NC}"

echo -e "${YELLOW}[4/5] Tool hardware & system...${NC}"
# termux-api per NFC, BLE scan, WiFi scan, device info
pkg install -y termux-api || true

# System Tools (alcuni in root-repo/x11-repo)
for pkg in nmap hydra john sqlmap gobuster ffuf dirb whatweb nikto whois dnsutils traceroute; do
  pkg install -y "$pkg" 2>/dev/null && echo -e "  ✅ $pkg" || echo -e "  ❌ $pkg"
done

# wfuzz via pip
pip install --break-system-packages wfuzz 2>/dev/null || pip install wfuzz 2>/dev/null || true

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
echo -e "${YELLOW}=== Riepilogo tool installati ===${NC}"
for cmd in termux-wifi-scaninfo termux-bluetooth-scan termux-nfc termux-battery-status nmap hydra john sqlmap gobuster ffuf dirb whatweb nikto dig whois blesh; do
  if command -v "$cmd" &>/dev/null; then echo -e "  ✅ $cmd"; else echo -e "  ❌ $cmd"; fi
done
for pkg in rich requests bleak pikepdf wfuzz; do
  if python -c "import $pkg" 2>/dev/null; then echo -e "  ✅ $pkg (Python)"; else echo -e "  ❌ $pkg (Python)"; fi
done

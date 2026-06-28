#!/bin/bash
"""
FLIPPER-Z ANDROID - Termux Installer
One-command setup script for Flipper Zero clone on Android
"""

set -e

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BIN_DIR="$PREFIX/bin"
APP_NAME="flipperz"

echo -e "${CYAN}"
echo "╔══════════════════════════════════════╗"
echo "║     FLIPPER-Z ANDROID INSTALLER      ║"
echo "║   Flipper Zero Clone for Termux      ║"
echo "╚══════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${YELLOW}[1/5] Updating packages...${NC}"
pkg update -y && pkg upgrade -y

echo -e "${YELLOW}[2/5] Installing dependencies...${NC}"
pkg install -y python python-pip git termux-api which

echo -e "${YELLOW}[3/5] Installing Python packages...${NC}"
pip install rich requests cryptography 2>/dev/null || pip install --break-system-packages rich requests cryptography 2>/dev/null || {
  echo -e "${YELLOW}⚠ pip non disponibile, installo via pkg...${NC}"
  pkg install -y python-rich python-requests || {
    echo -e "${RED}⚠ Installa manualmente: pip install rich requests cryptography${NC}"
  }
}

echo -e "${YELLOW}[4/5] Installing optional tools (WiFi/BLE)...${NC}"
echo -e "${CYAN}Installing aircrack-ng for WiFi attacks...${NC}"
pkg install -y aircrack-ng || echo -e "${RED}aircrack-ng not available in Termux${NC}"
pkg install -y nmap || echo -e "${RED}nmap not available in Termux${NC}"

echo -e "${YELLOW}[5/5] Installing Flipper-Z...${NC}"

# Create launcher script
LAUNCHER="$PREFIX/bin/$APP_NAME"
cat > "$LAUNCHER" << 'LAUNCHER_EOF'
#!/data/data/com.termux/files/usr/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FLIPPER_DIR="$HOME/flipperz-android"

# Find the actual install directory
if [ -d "$FLIPPER_DIR" ]; then
    cd "$FLIPPER_DIR"
elif [ -d "$HOME/../usr/share/flipperz-android" ]; then
    cd "$HOME/../usr/share/flipperz-android"
elif [ -d "/data/data/com.termux/files/home/flipperz-android" ]; then
    cd "/data/data/com.termux/files/home/flipperz-android"
else
    # Try parent directories
    for dir in "$HOME"/*/flipperz-android "$HOME"/flipperz* /data/data/com.termux/files/home/*/flipperz-android; do
        if [ -d "$dir" ]; then
            cd "$dir"
            break
        fi
    done
fi

# Set Python path
export PATH="$PATH:$PREFIX/bin"

# Run Flipper-Z
if [ -f "main.py" ]; then
    python main.py
else
    echo "Error: main.py not found!"
    echo "Searching..."
    find "$HOME" -name "main.py" -path "*/flipperz*" 2>/dev/null | head -5
    exit 1
fi
LAUNCHER_EOF

chmod +x "$LAUNCHER"

# Copy project to home directory
INSTALL_DIR="$HOME/flipperz-android"
if [ "$SCRIPT_DIR" != "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}Copying project to $INSTALL_DIR...${NC}"
    rm -rf "$INSTALL_DIR"
    cp -r "$SCRIPT_DIR" "$INSTALL_DIR"
fi

# Create data directories
mkdir -p "$INSTALL_DIR/data/nfc_tags"
mkdir -p "$INSTALL_DIR/data/ble"
mkdir -p "$INSTALL_DIR/data/wifi"
mkdir -p "$INSTALL_DIR/data/bruteforce"
mkdir -p "$INSTALL_DIR/data/subghz"
mkdir -p "$INSTALL_DIR/data/badusb"

# Check termux-api
echo -e "${CYAN}"
echo "Checking Termux-API setup..."
echo -e "${NC}"
if command -v termux-wifi-scaninfo &>/dev/null; then
    echo -e "${GREEN}✓ termux-api is installed${NC}"
else
    echo -e "${YELLOW}⚠ termux-api not found. Run: pkg install termux-api${NC}"
    echo -e "${YELLOW}  Then grant permissions in Android settings.${NC}"
fi

echo ""
echo -e "${GREEN}╔══════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     INSTALLATION COMPLETE! 🐬        ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}To run Flipper-Z:${NC}"
echo -e "  ${GREEN}flipperz${NC}"
echo ""
echo -e "${CYAN}Or directly:${NC}"
echo -e "  ${GREEN}cd ~/flipperz-android && python main.py${NC}"
echo ""
echo -e "${CYAN}Available tools:${NC}"
echo -e "  📡 NFC Tools       - Read/write/clone NFC tags"
echo -e "  🔵 BLE Scanner     - Bluetooth Low Energy attacks"
echo -e "  📶 WiFi Tools      - Scan, deauth, handshake"
echo -e "  ⚡ Brute Force     - PIN, password, UID brute forcing"
echo -e "  📻 Sub-GHz         - RF signal simulation"
echo -e "  ⌨️  BadUSB          - HID attack scripts"
echo ""
echo -e "${YELLOW}Note: Some features need:${NC}"
echo -e "  - NFC: Hardware NFC + termux-nfc"
echo -e "  - WiFi monitor mode: Root + aircrack-ng"
echo -e "  - BLE: termux-bluetooth-scan"
echo -e "  - Sub-GHz TX: CC1101 module or RTL-SDR"
echo ""

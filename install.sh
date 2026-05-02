#!/bin/bash
# ╔══════════════════════════════════════════════════════════════╗
# ║           CLAN NXT TOOLKIT - INSTALLATION SCRIPT            ║
# ║                  Cybersecurity Arsenal v1.0                 ║
# ╚══════════════════════════════════════════════════════════════╝

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'
BOLD='\033[1m'

echo -e "${RED}"
echo "  ██████╗██╗      █████╗ ███╗   ██╗    ███╗   ██╗██╗  ██╗████████╗"
echo " ██╔════╝██║     ██╔══██╗████╗  ██║    ████╗  ██║╚██╗██╔╝╚══██╔══╝"
echo " ██║     ██║     ███████║██╔██╗ ██║    ██╔██╗ ██║ ╚███╔╝    ██║   "
echo " ██║     ██║     ██╔══██║██║╚██╗██║    ██║╚██╗██║ ██╔██╗    ██║   "
echo " ╚██████╗███████╗██║  ██║██║ ╚████║    ██║ ╚████║██╔╝ ██╗   ██║   "
echo "  ╚═════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝    ╚═╝  ╚═══╝╚═╝  ╚═╝   ╚═╝   "
echo -e "${NC}"
echo -e "${CYAN}${BOLD}  ══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}           CLAN NXT Toolkit Installer v1.0${NC}"
echo -e "${CYAN}${BOLD}  ══════════════════════════════════════════════════════════${NC}"
echo ""

# Check root
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}[!] Running without root. Some features may not install correctly.${NC}"
    echo -e "${YELLOW}[!] Consider running: sudo bash install.sh${NC}"
    echo ""
fi

# Check Python 3
echo -e "${CYAN}[*] Checking Python 3...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[✗] Python 3 not found. Installing...${NC}"
    apt-get update && apt-get install -y python3 python3-pip
else
    PYVER=$(python3 --version)
    echo -e "${GREEN}[✓] $PYVER found${NC}"
fi

# Install pip if needed
echo -e "${CYAN}[*] Checking pip...${NC}"
if ! command -v pip3 &> /dev/null; then
    echo -e "${YELLOW}[!] pip3 not found. Installing...${NC}"
    apt-get install -y python3-pip 2>/dev/null || python3 -m ensurepip
fi
echo -e "${GREEN}[✓] pip3 available${NC}"

# Install Python dependencies
echo -e "${CYAN}[*] Installing Python dependencies...${NC}"
pip3 install -r requirements.txt --break-system-packages 2>/dev/null || pip3 install -r requirements.txt
echo -e "${GREEN}[✓] Python dependencies installed${NC}"

# Install system tools (Kali/Debian)
echo -e "${CYAN}[*] Checking system tools...${NC}"

TOOLS=("nmap" "nikto" "sqlmap" "whatweb" "dirb" "gobuster" "hydra" "john" "hashcat" "enum4linux" "smbclient" "netcat-openbsd" "curl" "wget" "whois" "dnsutils" "traceroute")

for tool in "${TOOLS[@]}"; do
    if command -v "$tool" &> /dev/null || dpkg -l "$tool" &> /dev/null 2>&1; then
        echo -e "  ${GREEN}[✓] $tool${NC}"
    else
        echo -e "  ${YELLOW}[~] $tool not found, attempting install...${NC}"
        apt-get install -y "$tool" 2>/dev/null
        if [ $? -eq 0 ]; then
            echo -e "  ${GREEN}[✓] $tool installed${NC}"
        else
            echo -e "  ${RED}[✗] $tool failed to install (install manually)${NC}"
        fi
    fi
done

# Create data directories
echo -e "${CYAN}[*] Setting up data directories...${NC}"
mkdir -p data
mkdir -p reports
mkdir -p logs
echo -e "${GREEN}[✓] Directories created${NC}"

# Make main script executable
chmod +x clan_nxt.py
echo -e "${GREEN}[✓] clan_nxt.py is now executable${NC}"

# Create symlink for easy access
if [ "$EUID" -eq 0 ]; then
    ln -sf "$(pwd)/clan_nxt.py" /usr/local/bin/clannxt 2>/dev/null
    echo -e "${GREEN}[✓] Symlink created: run 'clannxt' from anywhere${NC}"
fi

echo ""
echo -e "${GREEN}${BOLD}  ══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}${BOLD}  [✓] CLAN NXT Toolkit installed successfully!${NC}"
echo -e "${GREEN}${BOLD}  ══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${CYAN}  Usage:${NC}"
echo -e "    ${YELLOW}python3 clan_nxt.py${NC}       # Run from this directory"
echo -e "    ${YELLOW}clannxt${NC}                   # Run from anywhere (if root)"
echo ""
echo -e "${RED}${BOLD}  ⚠  FOR AUTHORIZED TESTING ONLY  ⚠${NC}"
echo -e "${CYAN}  Use responsibly. You are accountable for your actions.${NC}"
echo ""

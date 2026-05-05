# 🔴 CLAN NXT Toolkit

```
   ██████╗██╗      █████╗ ███╗   ██╗    ███╗   ██╗██╗  ██╗████████╗
  ██╔════╝██║     ██╔══██╗████╗  ██║    ████╗  ██║╚██╗██╔╝╚══██╔══╝
  ██║     ██║     ███████║██╔██╗ ██║    ██╔██╗ ██║ ╚███╔╝    ██║   
  ██║     ██║     ██╔══██║██║╚██╗██║    ██║╚██╗██║ ██╔██╗    ██║   
  ╚██████╗███████╗██║  ██║██║ ╚████║    ██║ ╚████║██╔╝ ██╗   ██║   
   ╚═════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝    ╚═╝  ╚═══╝╚═╝  ╚═╝   ╚═╝
```

> **Cybersecurity Toolkit v1.0** | **#CLAN NXT**

A comprehensive terminal-based cybersecurity arsenal designed for Kali Linux and penetration testing environments. Built with the same aesthetic and philosophy as the [C2 Infrastructure Manager](https://github.com/Codergoterrors/C2-Infrastructure-Manager).

---

## ⚡ Features

### 1. Payload Arsenal
- Pre-loaded with **8+ real-world CVE exploits** (Log4Shell, Spring4Shell, EternalBlue, Copy-Fail, etc.)
- **Clone & Run** payloads directly from GitHub
- Add, search, and manage custom payloads
- Full metadata: CVE, severity, language, usage instructions

### 2. Vulnerability Scanner
- **13 automated scan modules** for comprehensive web app testing:
  - Security Headers Analysis
  - SSL/TLS Configuration
  - Directory & Sensitive File Enumeration
  - **API Key & Secret Exposure Detection** (AWS, GitHub, OpenAI, DB URIs)
  - **SQL Injection Testing** (URL params + forms)
  - **Cross-Site Scripting (XSS)**
  - CORS Misconfiguration
  - Rate Limiting Tests
  - Open Redirect Detection
  - Clickjacking Protection
  - Cookie Security Analysis
  - Information Disclosure
  - HTTP Method Testing
- Generates detailed reports saved to `reports/`

### 3. Tools Library
- **30 pre-loaded tools** across 8 categories:
  - OSINT (Sherlock, theHarvester, SpiderFoot, Maltego, Recon-ng)
  - Social Engineering (SET, Gophish, King Phisher)
  - Reverse Engineering (Ghidra, Radare2, Binary Ninja, Cutter)
  - Web Testing (Burp Suite, OWASP ZAP, Nikto, SQLMap, WPScan)
  - Network (Nmap, Wireshark, Masscan, Responder)
  - Password Cracking (Hashcat, John the Ripper, Hydra)
  - Exploitation (Metasploit, SearchSploit, CrackMapExec)
  - Wireless (Aircrack-ng)
- Install tools directly from the menu
- Add custom tools to your library

### 4. Hackathon Mode
- **Automated Mode**: Full pipeline — network scan → port scan → service detection → vulnerability scan → exploitation → report
- **Manual Mode**: Interactive guided methodology with step-by-step attack suggestions based on:
  - Target OS
  - Network position
  - Discovered services
  - Linux/Windows privilege escalation paths

---

## 🚀 Installation

### Quick Install (Kali Linux)
```bash
git clone https://github.com/Codergoterrors/clan-nxt-toolkit.git
cd clan-nxt-toolkit
sudo bash install.sh
```

### Manual Install
```bash
pip3 install -r requirements.txt
chmod +x clan_nxt.py
python3 clan_nxt.py
```

---

## 📋 Usage

```bash
# Run from the project directory
python3 clan_nxt.py

# Or if installed globally (after install.sh with root)
clannxt
```

---

## 📁 Project Structure

```
clan-nxt-toolkit/
├── clan_nxt.py              # Main entry point
├── modules/
│   ├── banner.py            # Terminal UI components
│   ├── utils.py             # Shared utilities
│   ├── payloads.py          # Payload manager
│   ├── vuln_scanner.py      # Website vulnerability scanner
│   ├── tools.py             # Tools library
│   └── hackathon.py         # Hackathon mode
├── data/                    # Auto-created data storage
│   ├── payloads.json        # Saved payloads
│   ├── tools.json           # Saved tools
│   └── exploits/            # Cloned exploit repos
├── reports/                 # Scan reports
├── logs/                    # Activity logs
├── install.sh               # Installation script
├── requirements.txt         # Python dependencies
└── README.md
```

---

## ⚠️ Legal Disclaimer

This tool is designed for **AUTHORIZED security testing and educational purposes only**. Unauthorized access to computer systems is illegal. Always obtain proper written authorization before testing any system you do not own.

The developers assume **no liability** for misuse of this tool.

---

## 🏷️ Credits

**#CLAN NXT** | Built with Python 🐍 | Powered by Rich, Requests, BeautifulSoup, Nmap 

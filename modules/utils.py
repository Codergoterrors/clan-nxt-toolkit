#!/usr/bin/env python3
"""
CLAN NXT Toolkit - Utility Functions
Shared helpers for file I/O, network checks, and system operations.
"""

import os
import sys
import json
import subprocess
import socket
import re
from datetime import datetime
from pathlib import Path

# ═══════════════════════════════════════════════════════════
# PATH CONFIGURATION
# ═══════════════════════════════════════════════════════════
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
for d in [DATA_DIR, REPORTS_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

PAYLOADS_FILE = DATA_DIR / "payloads.json"
TOOLS_FILE = DATA_DIR / "tools.json"


# ═══════════════════════════════════════════════════════════
# FILE I/O
# ═══════════════════════════════════════════════════════════
def load_json(filepath):
    """Load JSON data from file."""
    filepath = Path(filepath)
    if filepath.exists():
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_json(filepath, data):
    """Save data to JSON file."""
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_report(report_name, content):
    """Save a scan report to the reports directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{report_name}_{timestamp}.txt"
    filepath = REPORTS_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return str(filepath)


def log_action(action, details=""):
    """Log an action to the log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = LOGS_DIR / f"clan_nxt_{datetime.now().strftime('%Y%m%d')}.log"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {action}: {details}\n")


# ═══════════════════════════════════════════════════════════
# NETWORK UTILITIES
# ═══════════════════════════════════════════════════════════
def is_valid_url(url):
    """Validate URL format."""
    pattern = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    return bool(pattern.match(url))


def is_valid_ip(ip):
    """Validate IP address format."""
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False


def resolve_hostname(hostname):
    """Resolve hostname to IP address."""
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return None


def check_port(host, port, timeout=3):
    """Check if a specific port is open."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def get_local_ip():
    """Get the local IP address of this machine."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def get_subnet():
    """Get the local subnet (e.g., 192.168.1.0/24)."""
    ip = get_local_ip()
    parts = ip.split(".")
    return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"


# ═══════════════════════════════════════════════════════════
# COMMAND EXECUTION
# ═══════════════════════════════════════════════════════════
def run_command(cmd, timeout=300, shell=True):
    """
    Run a shell command and return (returncode, stdout, stderr).
    """
    try:
        process = subprocess.Popen(
            cmd,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(timeout=timeout)
        return process.returncode, stdout, stderr
    except subprocess.TimeoutExpired:
        process.kill()
        return -1, "", "Command timed out"
    except FileNotFoundError:
        return -1, "", f"Command not found: {cmd}"
    except Exception as e:
        return -1, "", str(e)


def check_tool_installed(tool_name):
    """Check if a system tool is installed."""
    rc, _, _ = run_command(f"which {tool_name}" if os.name != "nt" else f"where {tool_name}")
    return rc == 0


def get_installed_tools():
    """Get a dict of common security tools and their install status."""
    tools = [
        "nmap", "nikto", "sqlmap", "whatweb", "dirb", "gobuster",
        "hydra", "john", "hashcat", "enum4linux", "smbclient",
        "netcat", "nc", "curl", "wget", "whois", "dig",
        "traceroute", "masscan", "wpscan", "searchsploit",
        "msfconsole", "burpsuite", "wireshark", "aircrack-ng",
        "recon-ng", "theharvester", "sherlock", "maltego",
    ]
    result = {}
    for tool in tools:
        result[tool] = check_tool_installed(tool)
    return result


# ═══════════════════════════════════════════════════════════
# FORMATTING HELPERS
# ═══════════════════════════════════════════════════════════
def truncate(text, max_len=60):
    """Truncate text with ellipsis."""
    if len(text) > max_len:
        return text[:max_len - 3] + "..."
    return text


def severity_color(severity):
    """Return ANSI color for severity level."""
    from modules.banner import C
    colors = {
        "critical": C.R,
        "high": C.R,
        "medium": C.Y,
        "low": C.CY,
        "info": C.GR,
    }
    return colors.get(severity.lower(), C.W)

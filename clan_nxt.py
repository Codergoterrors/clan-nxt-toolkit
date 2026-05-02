#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║                    CLAN NXT TOOLKIT v1.0                        ║
║              Cybersecurity Arsenal & Automation                 ║
║                                                                 ║
║  Modules:                                                       ║
║    [1] Payload Arsenal  - Manage & deploy exploits              ║
║    [2] Vuln Scanner     - Automated website security testing    ║
║    [3] Tools Library    - Curated cybersecurity tools            ║
║    [4] Hackathon Mode   - CTF/hackathon exploitation            ║
║                                                                 ║
║  Author: #CLAN NXT                                              ║
║  License: Educational Use Only                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.banner import (
    C, clear_screen, print_banner, print_header, print_menu_option,
    print_status, get_input, print_separator, print_disclaimer,
    typing_effect, loading_animation
)
from modules.utils import log_action, get_local_ip


def show_main_menu():
    """Display the main CLAN NXT menu."""
    print()
    print(f"  {C.R}╔══════════════════════════════════════════════════════╗{C.RST}")
    print(f"  {C.R}║{C.RST}                                                      {C.R}║{C.RST}")
    print(f"  {C.R}║{C.RST}   {C.W}{C.BOLD}[1]{C.RST} {C.R}⚡{C.RST} {C.W}Payload Arsenal{C.RST}                            {C.R}║{C.RST}")
    print(f"  {C.R}║{C.RST}       {C.GR}Manage & deploy exploit payloads{C.RST}               {C.R}║{C.RST}")
    print(f"  {C.R}║{C.RST}                                                      {C.R}║{C.RST}")
    print(f"  {C.R}║{C.RST}   {C.W}{C.BOLD}[2]{C.RST} {C.R}🛡{C.RST}  {C.W}Vulnerability Scanner{C.RST}                      {C.R}║{C.RST}")
    print(f"  {C.R}║{C.RST}       {C.GR}Automated website security testing{C.RST}             {C.R}║{C.RST}")
    print(f"  {C.R}║{C.RST}                                                      {C.R}║{C.RST}")
    print(f"  {C.R}║{C.RST}   {C.W}{C.BOLD}[3]{C.RST} {C.R}🔧{C.RST} {C.W}Tools Library{C.RST}                               {C.R}║{C.RST}")
    print(f"  {C.R}║{C.RST}       {C.GR}Curated cybersecurity toolkit{C.RST}                  {C.R}║{C.RST}")
    print(f"  {C.R}║{C.RST}                                                      {C.R}║{C.RST}")
    print(f"  {C.R}║{C.RST}   {C.W}{C.BOLD}[4]{C.RST} {C.R}🏴{C.RST} {C.W}Hackathon Mode{C.RST}                              {C.R}║{C.RST}")
    print(f"  {C.R}║{C.RST}       {C.GR}CTF & hackathon exploitation{C.RST}                   {C.R}║{C.RST}")
    print(f"  {C.R}║{C.RST}                                                      {C.R}║{C.RST}")
    print(f"  {C.R}║{C.RST}   {C.W}{C.BOLD}[5]{C.RST} {C.R}📊{C.RST} {C.W}System Info{C.RST}                                 {C.R}║{C.RST}")
    print(f"  {C.R}║{C.RST}       {C.GR}View system & network information{C.RST}              {C.R}║{C.RST}")
    print(f"  {C.R}║{C.RST}                                                      {C.R}║{C.RST}")
    print(f"  {C.R}║{C.RST}   {C.W}{C.BOLD}[0]{C.RST} {C.GR}Exit CLAN NXT{C.RST}                                  {C.R}║{C.RST}")
    print(f"  {C.R}║{C.RST}                                                      {C.R}║{C.RST}")
    print(f"  {C.R}╚══════════════════════════════════════════════════════╝{C.RST}")


def system_info():
    """Display system and network information."""
    import platform
    from modules.utils import run_command, get_local_ip, get_subnet

    print_header("SYSTEM INFORMATION")

    print(f"    {C.GR}OS:{C.RST}           {C.W}{platform.system()} {platform.release()}{C.RST}")
    print(f"    {C.GR}Machine:{C.RST}      {C.W}{platform.machine()}{C.RST}")
    print(f"    {C.GR}Hostname:{C.RST}     {C.W}{platform.node()}{C.RST}")
    print(f"    {C.GR}Python:{C.RST}       {C.W}{platform.python_version()}{C.RST}")
    print(f"    {C.GR}Local IP:{C.RST}     {C.CY}{get_local_ip()}{C.RST}")
    print(f"    {C.GR}Subnet:{C.RST}       {C.CY}{get_subnet()}{C.RST}")

    # Network interfaces
    print(f"\n    {C.GR}Network Interfaces:{C.RST}")
    if platform.system() == "Linux":
        rc, out, _ = run_command("ip -4 addr show | grep -E 'inet |^[0-9]'")
        if rc == 0:
            for line in out.strip().split("\n"):
                print(f"      {C.W}{line.strip()}{C.RST}")
    elif platform.system() == "Windows":
        rc, out, _ = run_command("ipconfig | findstr /i \"IPv4 Subnet\"")
        if rc == 0:
            for line in out.strip().split("\n"):
                print(f"      {C.W}{line.strip()}{C.RST}")

    # Check external IP
    print(f"\n    {C.GR}External IP:{C.RST}", end=" ")
    try:
        import requests
        r = requests.get("https://api.ipify.org", timeout=5)
        print(f"{C.CY}{r.text}{C.RST}")
    except:
        print(f"{C.Y}Could not determine{C.RST}")


def main():
    """Main entry point for CLAN NXT Toolkit."""
    try:
        print_banner()
        print_disclaimer()
        log_action("SESSION_START", f"IP: {get_local_ip()}")

        while True:
            show_main_menu()
            choice = get_input("CLAN-NXT")

            if choice == "1":
                from modules.payloads import payload_manager
                payload_manager()

            elif choice == "2":
                from modules.vuln_scanner import vuln_scanner_menu
                vuln_scanner_menu()

            elif choice == "3":
                from modules.tools import tools_manager
                tools_manager()

            elif choice == "4":
                from modules.hackathon import hackathon_mode
                hackathon_mode()

            elif choice == "5":
                system_info()
                get_input("enter")

            elif choice in ("0", "exit", "quit", "q"):
                print()
                typing_effect("  [SYS] Shutting down CLAN NXT Toolkit...", delay=0.02, color=C.R)
                typing_effect("  [SYS] Stay safe. Hack responsibly. #CLAN NXT", delay=0.02, color=C.GR)
                print()
                log_action("SESSION_END")
                sys.exit(0)

            elif choice == "clear":
                clear_screen()
                print_banner()

            elif choice == "help":
                print_header("HELP")
                print(f"    {C.W}1{C.RST} - Payload Arsenal (manage exploits)")
                print(f"    {C.W}2{C.RST} - Vulnerability Scanner (scan websites)")
                print(f"    {C.W}3{C.RST} - Tools Library (security tools)")
                print(f"    {C.W}4{C.RST} - Hackathon Mode (CTF/competitions)")
                print(f"    {C.W}5{C.RST} - System Information")
                print(f"    {C.W}clear{C.RST} - Clear screen")
                print(f"    {C.W}0/exit{C.RST} - Exit")
                get_input("enter")

            else:
                print_status(f"Unknown command: '{choice}'. Type 'help' for options.", "warning")

    except KeyboardInterrupt:
        print(f"\n\n  {C.R}[!]{C.RST} {C.Y}Interrupted. Exiting...{C.RST}")
        log_action("SESSION_INTERRUPT")
        sys.exit(0)
    except Exception as e:
        print(f"\n  {C.R}[FATAL]{C.RST} {e}")
        log_action("ERROR", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()

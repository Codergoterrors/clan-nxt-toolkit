#!/usr/bin/env python3
"""
CLAN NXT Toolkit - Banner & UI Components
Premium terminal aesthetics for the cybersecurity arsenal.
"""

import os
import sys
import time
import random
from datetime import datetime

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    from rich.columns import Columns
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

console = Console() if RICH_AVAILABLE else None

# ═══════════════════════════════════════════════════════════
# COLOR CODES (fallback when Rich isn't available)
# ═══════════════════════════════════════════════════════════
class C:
    """ANSI color codes for terminal output."""
    R = "\033[1;31m"      # Red
    G = "\033[1;32m"      # Green
    Y = "\033[1;33m"      # Yellow
    B = "\033[1;34m"      # Blue
    M = "\033[1;35m"      # Magenta
    CY = "\033[1;36m"     # Cyan
    W = "\033[1;37m"      # White
    GR = "\033[0;90m"     # Gray
    DR = "\033[0;31m"     # Dark Red
    DG = "\033[0;32m"     # Dark Green
    DY = "\033[0;33m"     # Dark Yellow
    DB = "\033[0;34m"     # Dark Blue
    DM = "\033[0;35m"     # Dark Magenta
    DC = "\033[0;36m"     # Dark Cyan
    RST = "\033[0m"       # Reset
    BOLD = "\033[1m"      # Bold
    DIM = "\033[2m"       # Dim
    UNDER = "\033[4m"     # Underline
    BLINK = "\033[5m"     # Blink


BANNER_ART = (
    f"\n{C.W}   ██████╗██╗      █████╗ ███╗   ██╗    {C.R}███╗   ██╗██╗  ██╗████████╗{C.RST}\n"
    f"{C.W}  ██╔════╝██║     ██╔══██╗████╗  ██║    {C.R}████╗  ██║╚██╗██╔╝╚══██╔══╝{C.RST}\n"
    f"{C.W}  ██║     ██║     ███████║██╔██╗ ██║    {C.R}██╔██╗ ██║ ╚███╔╝    ██║{C.RST}\n"
    f"{C.W}  ██║     ██║     ██╔══██║██║╚██╗██║    {C.R}██║╚██╗██║ ██╔██╗    ██║{C.RST}\n"
    f"{C.W}  ╚██████╗███████╗██║  ██║██║ ╚████║    {C.R}██║ ╚████║██╔╝ ██╗   ██║{C.RST}\n"
    f"{C.W}   ╚═════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝    {C.R}╚═╝  ╚═══╝╚═╝  ╚═╝   ╚═╝{C.RST}\n"
)

TAGLINE = f"{C.GR}  Cybersecurity Toolkit v1.0  {C.DIM}│{C.RST}  {C.W}#CLAN {C.R}NXT{C.RST} {C.GR}~{C.RST}"


def clear_screen():
    """Clear terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def typing_effect(text, delay=0.02, color=C.CY):
    """Print text with typing animation."""
    for char in text:
        sys.stdout.write(f"{color}{char}{C.RST}")
        sys.stdout.flush()
        time.sleep(delay)
    print()


def print_banner():
    """Display the main CLAN NXT banner."""
    clear_screen()
    print(BANNER_ART)
    print(TAGLINE)
    print()
    
    now = datetime.now().strftime("%H:%M:%S")
    typing_effect(f"  [{now}] [SYS] Initializing CLAN NXT Toolkit...", delay=0.01)
    time.sleep(0.3)
    
    # System info line
    user = os.getenv("USER", os.getenv("USERNAME", "operator"))
    print(f"  {C.GR}[{now}] [SYS] Operator: {C.CY}{user}{C.GR} | Platform: {C.CY}{sys.platform}{C.GR} | Python: {C.CY}{sys.version.split()[0]}{C.RST}")
    print()


def print_separator(char="═", length=65, color=C.GR):
    """Print a decorative separator line."""
    print(f"  {color}{char * length}{C.RST}")


def print_header(title, subtitle=""):
    """Print a section header."""
    print()
    print_separator()
    print(f"  {C.R}▸{C.RST} {C.W}{C.BOLD}{title}{C.RST}")
    if subtitle:
        print(f"    {C.GR}{subtitle}{C.RST}")
    print_separator()
    print()


def print_menu_option(number, title, description="", icon="▸"):
    """Print a styled menu option."""
    num_color = C.R
    title_color = C.W
    desc_color = C.GR
    print(f"    {num_color}[{number}]{C.RST} {C.R}{icon}{C.RST} {title_color}{title}{C.RST}")
    if description:
        print(f"         {desc_color}{description}{C.RST}")


def print_status(message, status="info"):
    """Print a status message with icon."""
    now = datetime.now().strftime("%H:%M:%S")
    icons = {
        "info":    (C.CY, "ℹ"),
        "success": (C.G, "✓"),
        "warning": (C.Y, "⚠"),
        "error":   (C.R, "✗"),
        "working": (C.M, "⟳"),
        "attack":  (C.R, "⚡"),
        "found":   (C.G, "◉"),
        "scan":    (C.CY, "◎"),
    }
    color, icon = icons.get(status, (C.W, "•"))
    print(f"  {C.GR}[{now}]{C.RST} {color}[{icon}]{C.RST} {message}")


def print_result_box(title, content, border_color=C.CY):
    """Print content inside a bordered box."""
    lines = content.split("\n")
    max_len = max(len(line) for line in lines + [title]) + 4
    
    print(f"\n  {border_color}╔{'═' * max_len}╗{C.RST}")
    print(f"  {border_color}║{C.RST} {C.W}{C.BOLD}{title.center(max_len - 2)}{C.RST} {border_color}║{C.RST}")
    print(f"  {border_color}╠{'═' * max_len}╣{C.RST}")
    for line in lines:
        padded = line.ljust(max_len - 2)
        print(f"  {border_color}║{C.RST} {padded} {border_color}║{C.RST}")
    print(f"  {border_color}╚{'═' * max_len}╝{C.RST}\n")


def get_input(prompt_text="CLAN-NXT"):
    """Get user input with styled prompt."""
    try:
        return input(f"\n  {C.R}┌──({C.W}{prompt_text}{C.R})\n  └──╼ {C.CY}${C.RST} ").strip()
    except (KeyboardInterrupt, EOFError):
        print()
        return ""


def print_progress_bar(current, total, prefix="Progress", length=40):
    """Print a progress bar."""
    filled = int(length * current // total)
    bar = f"{C.R}{'█' * filled}{C.GR}{'░' * (length - filled)}{C.RST}"
    percent = f"{100 * current / total:.1f}"
    print(f"\r  {C.GR}{prefix}{C.RST} [{bar}] {C.W}{percent}%{C.RST}", end="", flush=True)
    if current == total:
        print()


def print_table(headers, rows, title=""):
    """Print a formatted table."""
    if RICH_AVAILABLE and console:
        table = Table(
            title=title if title else None,
            box=box.DOUBLE_EDGE,
            border_style="red",
            header_style="bold white on dark_red",
            title_style="bold red",
        )
        for h in headers:
            table.add_column(h, style="cyan")
        for row in rows:
            table.add_row(*[str(cell) for cell in row])
        console.print(table)
    else:
        # Fallback ASCII table
        if title:
            print(f"\n  {C.W}{C.BOLD}{title}{C.RST}")
        col_widths = [max(len(str(h)), max((len(str(row[i])) for row in rows), default=0)) + 2 for i, h in enumerate(headers)]
        
        header_line = "  " + " │ ".join(h.center(w) for h, w in zip(headers, col_widths))
        sep_line = "  " + "─┼─".join("─" * w for w in col_widths)
        
        print(f"  {C.GR}{'─' * (sum(col_widths) + 3 * (len(headers) - 1))}{C.RST}")
        print(f"  {C.W}{C.BOLD}{header_line.strip()}{C.RST}")
        print(f"  {C.GR}{sep_line.strip()}{C.RST}")
        for row in rows:
            row_line = "  " + " │ ".join(str(cell).ljust(w) for cell, w in zip(row, col_widths))
            print(f"  {C.CY}{row_line.strip()}{C.RST}")
        print(f"  {C.GR}{'─' * (sum(col_widths) + 3 * (len(headers) - 1))}{C.RST}")


def loading_animation(text="Loading", duration=1.5):
    """Show a loading animation."""
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        frame = frames[i % len(frames)]
        print(f"\r  {C.R}{frame}{C.RST} {C.CY}{text}...{C.RST}", end="", flush=True)
        time.sleep(0.08)
        i += 1
    print(f"\r  {C.G}✓{C.RST} {C.CY}{text}... Done{C.RST}   ")


def confirm_action(message):
    """Ask for confirmation."""
    response = input(f"\n  {C.Y}[?]{C.RST} {message} {C.GR}(y/N):{C.RST} ").strip().lower()
    return response in ("y", "yes")


def print_disclaimer():
    """Print legal disclaimer."""
    print(f"""
  {C.R}{'═' * 65}{C.RST}
  {C.R}{C.BOLD}⚠  LEGAL DISCLAIMER  ⚠{C.RST}
  {C.R}{'═' * 65}{C.RST}
  {C.Y}This tool is designed for AUTHORIZED security testing only.{C.RST}
  {C.Y}Unauthorized access to computer systems is illegal.{C.RST}
  {C.Y}The developers assume no liability for misuse.{C.RST}
  {C.Y}Always obtain proper authorization before testing.{C.RST}
  {C.R}{'═' * 65}{C.RST}
""")

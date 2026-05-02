#!/usr/bin/env python3
"""
CLAN NXT Toolkit - Tools Manager
Curated library of cybersecurity tools organized by category.
"""

from datetime import datetime
from modules.banner import (
    C, clear_screen, print_header, print_menu_option, print_status,
    get_input, print_table, print_separator, print_result_box, confirm_action
)
from modules.utils import load_json, save_json, TOOLS_FILE, run_command, log_action, check_tool_installed

DEFAULT_TOOLS = {"tools": [
    # OSINT
    {"id":1,"name":"Sherlock","category":"OSINT","description":"Hunt usernames across 400+ social networks",
     "install":"pip3 install sherlock-project","usage":"sherlock <username>","url":"https://github.com/sherlock-project/sherlock","installed":False},
    {"id":2,"name":"theHarvester","category":"OSINT","description":"Email, subdomain and name harvester from public sources",
     "install":"apt install theharvester","usage":"theHarvester -d <domain> -b all","url":"https://github.com/laramies/theHarvester","installed":False},
    {"id":3,"name":"SpiderFoot","category":"OSINT","description":"Automated OSINT collection with 200+ modules",
     "install":"pip3 install spiderfoot","usage":"spiderfoot -l 127.0.0.1:5001","url":"https://github.com/smicallef/spiderfoot","installed":False},
    {"id":4,"name":"Maltego","category":"OSINT","description":"Interactive data mining and link analysis",
     "install":"apt install maltego","usage":"maltego","url":"https://www.maltego.com/","installed":False},
    {"id":5,"name":"Recon-ng","category":"OSINT","description":"Full-featured web reconnaissance framework",
     "install":"apt install recon-ng","usage":"recon-ng","url":"https://github.com/lanmaster53/recon-ng","installed":False},
    {"id":6,"name":"Holehe","category":"OSINT","description":"Check if email is used on various sites",
     "install":"pip3 install holehe","usage":"holehe <email>","url":"https://github.com/megadose/holehe","installed":False},
    {"id":7,"name":"PhoneInfoga","category":"OSINT","description":"Advanced phone number OSINT scanner",
     "install":"go install github.com/sundowndev/phoneinfoga/v2@latest","usage":"phoneinfoga scan -n <number>","url":"https://github.com/sundowndev/phoneinfoga","installed":False},
    # Social Engineering
    {"id":8,"name":"Social Engineering Toolkit (SET)","category":"Social Engineering","description":"Framework for social engineering attacks",
     "install":"apt install set","usage":"setoolkit","url":"https://github.com/trustedsec/social-engineer-toolkit","installed":False},
    {"id":9,"name":"Gophish","category":"Social Engineering","description":"Open-source phishing framework for awareness testing",
     "install":"Download from https://github.com/gophish/gophish/releases","usage":"./gophish","url":"https://github.com/gophish/gophish","installed":False},
    {"id":10,"name":"King Phisher","category":"Social Engineering","description":"Phishing campaign toolkit with detailed analytics",
     "install":"apt install king-phisher","usage":"king-phisher","url":"https://github.com/securestate/king-phisher","installed":False},
    # Reverse Engineering
    {"id":11,"name":"Ghidra","category":"Reverse Engineering","description":"NSA's software reverse engineering framework",
     "install":"apt install ghidra","usage":"ghidra","url":"https://github.com/NationalSecurityAgency/ghidra","installed":False},
    {"id":12,"name":"Radare2","category":"Reverse Engineering","description":"Unix-like reverse engineering framework and CLI tools",
     "install":"apt install radare2","usage":"r2 <binary>","url":"https://github.com/radareorg/radare2","installed":False},
    {"id":13,"name":"Binary Ninja","category":"Reverse Engineering","description":"Interactive binary analysis platform",
     "install":"https://binary.ninja/","usage":"binaryninja","url":"https://binary.ninja/","installed":False},
    {"id":14,"name":"Cutter","category":"Reverse Engineering","description":"GUI for Rizin reverse engineering framework",
     "install":"apt install cutter","usage":"cutter","url":"https://github.com/rizinorg/cutter","installed":False},
    # Web Testing
    {"id":15,"name":"Burp Suite","category":"Web Testing","description":"Web application security testing platform",
     "install":"apt install burpsuite","usage":"burpsuite","url":"https://portswigger.net/burp","installed":False},
    {"id":16,"name":"OWASP ZAP","category":"Web Testing","description":"Open-source web app scanner",
     "install":"apt install zaproxy","usage":"zaproxy","url":"https://www.zaproxy.org/","installed":False},
    {"id":17,"name":"Nikto","category":"Web Testing","description":"Web server vulnerability scanner",
     "install":"apt install nikto","usage":"nikto -h <target>","url":"https://github.com/sullo/nikto","installed":False},
    {"id":18,"name":"SQLMap","category":"Web Testing","description":"Automatic SQL injection and database takeover tool",
     "install":"apt install sqlmap","usage":"sqlmap -u <url> --dbs","url":"https://github.com/sqlmapproject/sqlmap","installed":False},
    {"id":19,"name":"WPScan","category":"Web Testing","description":"WordPress security scanner",
     "install":"apt install wpscan","usage":"wpscan --url <target>","url":"https://github.com/wpscanteam/wpscan","installed":False},
    # Network
    {"id":20,"name":"Nmap","category":"Network","description":"Network discovery and security auditing",
     "install":"apt install nmap","usage":"nmap -sV -sC <target>","url":"https://nmap.org/","installed":False},
    {"id":21,"name":"Wireshark","category":"Network","description":"Network protocol analyzer and packet capture",
     "install":"apt install wireshark","usage":"wireshark","url":"https://www.wireshark.org/","installed":False},
    {"id":22,"name":"Masscan","category":"Network","description":"Fastest Internet port scanner",
     "install":"apt install masscan","usage":"masscan <target> -p1-65535 --rate=1000","url":"https://github.com/robertdavidgraham/masscan","installed":False},
    {"id":23,"name":"Responder","category":"Network","description":"LLMNR/NBT-NS/MDNS poisoner for credential capture",
     "install":"apt install responder","usage":"responder -I eth0","url":"https://github.com/lgandx/Responder","installed":False},
    # Password/Cracking
    {"id":24,"name":"Hashcat","category":"Password","description":"Advanced GPU-based password recovery",
     "install":"apt install hashcat","usage":"hashcat -m 0 <hash_file> <wordlist>","url":"https://hashcat.net/hashcat/","installed":False},
    {"id":25,"name":"John the Ripper","category":"Password","description":"Password cracker supporting many hash types",
     "install":"apt install john","usage":"john --wordlist=<wordlist> <hash_file>","url":"https://www.openwall.com/john/","installed":False},
    {"id":26,"name":"Hydra","category":"Password","description":"Online password brute-force tool",
     "install":"apt install hydra","usage":"hydra -l <user> -P <wordlist> <target> ssh","url":"https://github.com/vanhauser-thc/thc-hydra","installed":False},
    # Exploitation
    {"id":27,"name":"Metasploit Framework","category":"Exploitation","description":"World's most used penetration testing framework",
     "install":"apt install metasploit-framework","usage":"msfconsole","url":"https://github.com/rapid7/metasploit-framework","installed":False},
    {"id":28,"name":"SearchSploit","category":"Exploitation","description":"CLI search for Exploit-DB archive",
     "install":"apt install exploitdb","usage":"searchsploit <keyword>","url":"https://www.exploit-db.com/searchsploit","installed":False},
    {"id":29,"name":"CrackMapExec","category":"Exploitation","description":"Swiss army knife for network pentesting",
     "install":"pip3 install crackmapexec","usage":"crackmapexec smb <target>","url":"https://github.com/byt3bl33d3r/CrackMapExec","installed":False},
    # Wireless
    {"id":30,"name":"Aircrack-ng","category":"Wireless","description":"WiFi security auditing tools suite",
     "install":"apt install aircrack-ng","usage":"airmon-ng start wlan0","url":"https://www.aircrack-ng.org/","installed":False},
]}

def init_tools():
    if not TOOLS_FILE.exists():
        save_json(TOOLS_FILE, DEFAULT_TOOLS)
    data = load_json(TOOLS_FILE)
    if not data or "tools" not in data:
        save_json(TOOLS_FILE, DEFAULT_TOOLS)
        return DEFAULT_TOOLS
    return data

def list_tools_by_category(data):
    tools = data.get("tools",[])
    categories = {}
    for t in tools:
        cat = t.get("category","General")
        categories.setdefault(cat,[]).append(t)
    print_header("TOOLS LIBRARY", f"{len(tools)} tools across {len(categories)} categories")
    for cat, items in sorted(categories.items()):
        print(f"\n  {C.R}━━━ {C.W}{C.BOLD}{cat.upper()}{C.RST} {C.R}━━━{C.RST}")
        for t in items:
            status = f"{C.G}[✓]{C.RST}" if t.get("installed") else f"{C.GR}[○]{C.RST}"
            print(f"    {status} {C.CY}[{t['id']:>2}]{C.RST} {C.W}{t['name']}{C.RST} {C.GR}- {t['description'][:50]}{C.RST}")

def view_tool_detail(data, tool_id):
    tool = next((t for t in data.get("tools",[]) if t["id"]==tool_id), None)
    if not tool: print_status("Not found.","error"); return
    print_header(f"TOOL: {tool['name']}")
    for k,v in [("Category",tool.get("category")),("Description",tool.get("description")),
                ("Install",tool.get("install")),("Usage",tool.get("usage")),("URL",tool.get("url"))]:
        print(f"    {C.GR}{k}:{C.RST} {C.W}{v}{C.RST}")
    print()
    print_menu_option("1","Install this tool"); print_menu_option("2","Run this tool"); print_menu_option("0","Back")
    ch = get_input(f"tool/{tool['name'][:12]}")
    if ch=="1":
        cmd = tool.get("install","")
        if cmd and confirm_action(f"Run: {cmd}?"):
            print_status(f"Installing {tool['name']}...","working")
            rc,out,err = run_command(cmd, timeout=120)
            print(out if out else err)
            if rc==0:
                tool["installed"]=True; save_json(TOOLS_FILE,data)
                print_status("Installed!","success")
            else: print_status(f"Failed: {err[:100]}","error")
    elif ch=="2":
        usage = tool.get("usage","")
        print_status(f"Usage: {C.W}{usage}{C.RST}","info")
        print_status("Customize the command and run in your terminal.","info")

def add_tool(data):
    print_header("ADD NEW TOOL")
    name=input(f"  {C.CY}Name:{C.RST} ").strip()
    if not name: print_status("Required.","error"); return data
    cat=input(f"  {C.CY}Category:{C.RST} ").strip() or "General"
    desc=input(f"  {C.CY}Description:{C.RST} ").strip()
    install=input(f"  {C.CY}Install command:{C.RST} ").strip()
    usage=input(f"  {C.CY}Usage command:{C.RST} ").strip()
    url=input(f"  {C.CY}URL:{C.RST} ").strip()
    nid=max((t["id"] for t in data.get("tools",[])),default=0)+1
    data["tools"].append({"id":nid,"name":name,"category":cat,"description":desc,
        "install":install,"usage":usage,"url":url,"installed":False})
    save_json(TOOLS_FILE,data)
    print_status(f"Tool '{name}' added (ID:{nid})","success")
    return data

def search_tools(data):
    q=input(f"  {C.CY}Search:{C.RST} ").strip().lower()
    if not q: return
    results=[t for t in data.get("tools",[]) if q in f"{t['name']} {t.get('category','')} {t.get('description','')}".lower()]
    if not results: print_status("No matches.","warning"); return
    for t in results:
        print(f"    {C.CY}[{t['id']:>2}]{C.RST} {C.W}{t['name']}{C.RST} ({t.get('category','')}) - {t.get('description','')[:50]}")

def tools_manager():
    data = init_tools()
    while True:
        clear_screen()
        print(f"\n{C.R}  ╔══════════════════════════════════════════════════╗{C.RST}")
        print(f"{C.R}  ║{C.RST}  {C.W}{C.BOLD}🔧 TOOLS LIBRARY{C.RST}                                {C.R}║{C.RST}")
        print(f"{C.R}  ╚══════════════════════════════════════════════════╝{C.RST}\n")
        print_menu_option("1","Browse All Tools","View by category")
        print_menu_option("2","View Tool Details","Install & usage info")
        print_menu_option("3","Add New Tool","Save a custom tool")
        print_menu_option("4","Search Tools","Find by keyword")
        print_menu_option("5","Check Installed","Verify system tools")
        print_menu_option("0","Back to Main Menu")
        ch = get_input("tools")
        if ch=="1": data=init_tools(); list_tools_by_category(data); get_input("enter")
        elif ch=="2":
            list_tools_by_category(data)
            try: view_tool_detail(data,int(input(f"\n  {C.CY}Tool ID:{C.RST} ")))
            except: print_status("Invalid.","error")
            get_input("enter")
        elif ch=="3": data=add_tool(data); get_input("enter")
        elif ch=="4": search_tools(data); get_input("enter")
        elif ch=="5":
            print_header("INSTALLED TOOLS CHECK")
            check_list = ["nmap","nikto","sqlmap","hydra","john","hashcat","msfconsole","aircrack-ng","gobuster","enum4linux","whatweb","wpscan","searchsploit","recon-ng","wireshark","masscan","responder","sherlock","theharvester"]
            for t in check_list:
                installed = check_tool_installed(t)
                s = f"{C.G}[✓] {t}{C.RST}" if installed else f"{C.R}[✗] {t}{C.RST}"
                print(f"    {s}")
            get_input("enter")
        elif ch in ("0","back","exit"): break

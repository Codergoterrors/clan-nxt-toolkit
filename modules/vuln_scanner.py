#!/usr/bin/env python3
"""
CLAN NXT Toolkit - Website Vulnerability Scanner
Automated security assessment for web applications.
"""

import re
import time
import json
import socket
import ssl
import hashlib
from datetime import datetime
from urllib.parse import urlparse, urljoin, quote
from pathlib import Path

try:
    import requests
    from requests.exceptions import RequestException, Timeout, ConnectionError
    REQUESTS_OK = True
except ImportError:
    REQUESTS_OK = False

try:
    from bs4 import BeautifulSoup
    BS4_OK = True
except ImportError:
    BS4_OK = False

from modules.banner import (
    C, clear_screen, print_header, print_menu_option, print_status,
    get_input, print_table, print_separator, print_result_box,
    loading_animation, print_progress_bar, confirm_action
)
from modules.utils import (
    is_valid_url, run_command, save_report, log_action, REPORTS_DIR
)

COMMON_DIRS = [
    "admin","administrator","login","wp-admin","wp-login.php","panel",
    "dashboard","api","api/v1","api/v2","graphql","swagger","docs",
    ".env",".git",".git/config",".svn","backup","db","database",
    "config","config.php","wp-config.php","robots.txt","sitemap.xml",
    "server-status","server-info",".htaccess",".htpasswd","phpinfo.php",
    "info.php","test","debug","console","shell","uploads","temp",
    "phpmyadmin","adminer","mailman","webmail","cpanel",
]

SQLI_PAYLOADS = [
    "' OR '1'='1", "' OR '1'='1' --", "' OR '1'='1' /*",
    "\" OR \"1\"=\"1\"", "' UNION SELECT NULL--",
    "1' ORDER BY 1--", "' AND 1=1--", "'; DROP TABLE users--",
    "1 OR 1=1", "' OR ''='", "admin'--",
]

XSS_PAYLOADS = [
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert('XSS')>",
    "<svg onload=alert('XSS')>",
    "'\"><script>alert(1)</script>",
    "javascript:alert('XSS')",
    "<body onload=alert('XSS')>",
    "<iframe src=\"javascript:alert('XSS')\">",
    "{{7*7}}", "${7*7}", "<%=7*7%>",
]

API_KEY_PATTERNS = [
    (r'(?:api[_-]?key|apikey|api_secret)\s*[:=]\s*["\']?([A-Za-z0-9_\-]{20,})', "API Key"),
    (r'(?:aws_access_key_id)\s*[:=]\s*["\']?([A-Z0-9]{20})', "AWS Access Key"),
    (r'(?:aws_secret_access_key)\s*[:=]\s*["\']?([A-Za-z0-9/+=]{40})', "AWS Secret"),
    (r'AKIA[0-9A-Z]{16}', "AWS Key ID"),
    (r'(?:github[_-]?token|gh_token)\s*[:=]\s*["\']?([a-zA-Z0-9_]{35,})', "GitHub Token"),
    (r'(?:sk-[a-zA-Z0-9]{20,})', "OpenAI Key"),
    (r'(?:Bearer\s+)([A-Za-z0-9\-._~+/]+=*)', "Bearer Token"),
    (r'(?:password|passwd|pwd)\s*[:=]\s*["\']([^"\']{4,})["\']', "Hardcoded Password"),
    (r'(?:secret|private[_-]?key)\s*[:=]\s*["\']?([A-Za-z0-9_\-]{16,})', "Secret Key"),
    (r'mongodb(?:\+srv)?://[^\s<>"]+', "MongoDB URI"),
    (r'postgres(?:ql)?://[^\s<>"]+', "PostgreSQL URI"),
    (r'mysql://[^\s<>"]+', "MySQL URI"),
]

SECURITY_HEADERS = [
    "Strict-Transport-Security", "Content-Security-Policy",
    "X-Content-Type-Options", "X-Frame-Options", "X-XSS-Protection",
    "Referrer-Policy", "Permissions-Policy", "Cross-Origin-Opener-Policy",
    "Cross-Origin-Resource-Policy", "Cross-Origin-Embedder-Policy",
]


class VulnScanner:
    def __init__(self, target_url):
        self.target = target_url.rstrip("/")
        self.parsed = urlparse(self.target)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })
        self.session.verify = False
        self.findings = []
        self.scanned_urls = set()
        self.start_time = datetime.now()

    def add_finding(self, title, severity, details, evidence=""):
        self.findings.append({
            "title": title, "severity": severity,
            "details": details, "evidence": evidence,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        sc = {"CRITICAL":C.R,"HIGH":C.R,"MEDIUM":C.Y,"LOW":C.CY,"INFO":C.GR}
        color = sc.get(severity, C.W)
        status = "attack" if severity in ("CRITICAL","HIGH") else "found" if severity=="MEDIUM" else "info"
        print_status(f"{color}[{severity}]{C.RST} {title}", status)

    def safe_get(self, url, timeout=10, allow_redirects=True):
        try:
            return self.session.get(url, timeout=timeout, allow_redirects=allow_redirects)
        except:
            return None

    def safe_post(self, url, data=None, timeout=10):
        try:
            return self.session.post(url, data=data, timeout=timeout)
        except:
            return None

    # ─── SCAN MODULES ───────────────────────────────────────
    def scan_security_headers(self):
        print_status("Checking security headers...", "scan")
        resp = self.safe_get(self.target)
        if not resp: return
        missing = [h for h in SECURITY_HEADERS if h.lower() not in {k.lower() for k in resp.headers}]
        if missing:
            self.add_finding("Missing Security Headers", "MEDIUM",
                f"Missing: {', '.join(missing)}", str(missing))
        server = resp.headers.get("Server","")
        if server:
            self.add_finding("Server Header Exposed", "LOW",
                f"Server: {server}", server)
        powered = resp.headers.get("X-Powered-By","")
        if powered:
            self.add_finding("X-Powered-By Exposed", "LOW",
                f"Technology: {powered}", powered)

    def scan_ssl_tls(self):
        print_status("Checking SSL/TLS configuration...", "scan")
        if self.parsed.scheme != "https":
            self.add_finding("No HTTPS", "HIGH", "Site does not use HTTPS encryption.")
            return
        try:
            ctx = ssl.create_default_context()
            with ctx.wrap_socket(socket.socket(), server_hostname=self.parsed.hostname) as s:
                s.settimeout(5)
                s.connect((self.parsed.hostname, 443))
                cert = s.getpeercert()
                expire = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
                if expire < datetime.now():
                    self.add_finding("Expired SSL Certificate", "HIGH",
                        f"Expired: {cert['notAfter']}")
                elif (expire - datetime.now()).days < 30:
                    self.add_finding("SSL Cert Expiring Soon", "MEDIUM",
                        f"Expires: {cert['notAfter']}")
        except Exception as e:
            self.add_finding("SSL/TLS Issue", "MEDIUM", str(e))

    def scan_directory_enum(self):
        print_status("Enumerating directories & sensitive files...", "scan")
        found = []
        total = len(COMMON_DIRS)
        for i, path in enumerate(COMMON_DIRS):
            print_progress_bar(i+1, total, "Dir Enum")
            url = f"{self.target}/{path}"
            resp = self.safe_get(url, timeout=5, allow_redirects=False)
            if resp and resp.status_code in (200, 301, 302, 403):
                found.append((path, resp.status_code))
                sev = "HIGH" if path in (".env",".git",".git/config",".htpasswd","wp-config.php") else \
                      "MEDIUM" if resp.status_code in (200,301,302) else "LOW"
                self.add_finding(f"Found: /{path}", sev,
                    f"Status {resp.status_code}", url)

    def scan_api_keys(self):
        print_status("Scanning for exposed API keys & secrets...", "scan")
        pages = [self.target]
        resp = self.safe_get(self.target)
        if resp and BS4_OK:
            soup = BeautifulSoup(resp.text, "html.parser")
            for script in soup.find_all("script", src=True):
                src = script["src"]
                if src.startswith("/"): src = f"{self.target}{src}"
                elif not src.startswith("http"): src = f"{self.target}/{src}"
                pages.append(src)
            for script in soup.find_all("script", src=False):
                if script.string:
                    for pattern, name in API_KEY_PATTERNS:
                        matches = re.findall(pattern, script.string)
                        if matches:
                            self.add_finding(f"Exposed {name} in Inline Script", "CRITICAL",
                                f"Found {len(matches)} occurrence(s)", matches[0][:30]+"...")
        for page in pages[:20]:
            resp = self.safe_get(page, timeout=5)
            if not resp: continue
            for pattern, name in API_KEY_PATTERNS:
                matches = re.findall(pattern, resp.text)
                if matches:
                    self.add_finding(f"Exposed {name}", "CRITICAL",
                        f"Found in {page}", matches[0][:30]+"...")

    def scan_sql_injection(self):
        print_status("Testing for SQL Injection vulnerabilities...", "scan")
        resp = self.safe_get(self.target)
        if not resp or not BS4_OK: return
        soup = BeautifulSoup(resp.text, "html.parser")
        forms = soup.find_all("form")
        test_params = [("id","1"),("page","1"),("search","test"),("q","test"),("user","admin")]
        # Test URL parameters
        for param, val in test_params:
            for payload in SQLI_PAYLOADS[:5]:
                url = f"{self.target}?{param}={quote(payload)}"
                r = self.safe_get(url, timeout=5)
                if r:
                    indicators = ["sql","syntax","mysql","postgresql","sqlite","oracle",
                                "warning","error in your","unclosed quotation"]
                    if any(ind in r.text.lower() for ind in indicators):
                        self.add_finding("SQL Injection (URL Param)", "CRITICAL",
                            f"Param: {param}, Payload: {payload}", url)
                        return
        # Test forms
        for form in forms[:5]:
            action = form.get("action","")
            action_url = urljoin(self.target, action) if action else self.target
            inputs = form.find_all("input")
            for payload in SQLI_PAYLOADS[:3]:
                data = {}
                for inp in inputs:
                    name = inp.get("name","")
                    if name: data[name] = payload
                r = self.safe_post(action_url, data=data, timeout=5)
                if r:
                    if any(ind in r.text.lower() for ind in ["sql","syntax","mysql","error"]):
                        self.add_finding("SQL Injection (Form)", "CRITICAL",
                            f"Form: {action_url}", str(data))
                        return

    def scan_xss(self):
        print_status("Testing for XSS vulnerabilities...", "scan")
        test_params = ["search","q","query","name","input","msg","comment","text"]
        for param in test_params:
            for payload in XSS_PAYLOADS[:4]:
                url = f"{self.target}?{param}={quote(payload)}"
                r = self.safe_get(url, timeout=5)
                if r and payload in r.text:
                    self.add_finding("Reflected XSS", "HIGH",
                        f"Param: {param}", payload[:50])
                    return

    def scan_cors(self):
        print_status("Checking CORS configuration...", "scan")
        headers = {"Origin": "https://evil-attacker.com"}
        try:
            r = self.session.get(self.target, headers=headers, timeout=5)
            acao = r.headers.get("Access-Control-Allow-Origin","")
            if acao == "*":
                self.add_finding("Wildcard CORS", "MEDIUM",
                    "Access-Control-Allow-Origin: *", acao)
            elif "evil-attacker.com" in acao:
                self.add_finding("CORS Origin Reflection", "HIGH",
                    "Server reflects arbitrary origins", acao)
            creds = r.headers.get("Access-Control-Allow-Credentials","")
            if creds.lower() == "true" and acao != "":
                self.add_finding("CORS with Credentials", "HIGH",
                    "Allows credentials from external origins")
        except: pass

    def scan_rate_limiting(self):
        print_status("Testing rate limiting...", "scan")
        endpoint = self.target
        resp = self.safe_get(self.target)
        if resp and BS4_OK:
            soup = BeautifulSoup(resp.text, "html.parser")
            forms = soup.find_all("form")
            for f in forms:
                if any(kw in str(f).lower() for kw in ["login","signin","password"]):
                    action = f.get("action","")
                    endpoint = urljoin(self.target, action) if action else self.target
                    break
        blocked = False
        for i in range(25):
            r = self.safe_get(endpoint, timeout=3)
            if r and r.status_code in (429, 503):
                blocked = True; break
        if not blocked:
            self.add_finding("No Rate Limiting", "MEDIUM",
                "25 rapid requests went through without throttling", endpoint)

    def scan_open_redirect(self):
        print_status("Testing for open redirects...", "scan")
        params = ["url","redirect","next","return","redir","dest","destination","go","target","link"]
        for param in params:
            url = f"{self.target}?{param}=https://evil.com"
            r = self.safe_get(url, timeout=5, allow_redirects=False)
            if r and r.status_code in (301,302,303,307,308):
                loc = r.headers.get("Location","")
                if "evil.com" in loc:
                    self.add_finding("Open Redirect", "MEDIUM",
                        f"Param: {param}", loc)
                    return

    def scan_clickjacking(self):
        print_status("Checking clickjacking protection...", "scan")
        r = self.safe_get(self.target)
        if r:
            xfo = r.headers.get("X-Frame-Options","")
            csp = r.headers.get("Content-Security-Policy","")
            if not xfo and "frame-ancestors" not in csp:
                self.add_finding("Clickjacking Possible", "MEDIUM",
                    "No X-Frame-Options or CSP frame-ancestors")

    def scan_cookies(self):
        print_status("Analyzing cookies...", "scan")
        r = self.safe_get(self.target)
        if not r: return
        for cookie in r.cookies:
            issues = []
            if not cookie.secure: issues.append("Missing Secure flag")
            if not cookie.has_nonstandard_attr("HttpOnly"): issues.append("Missing HttpOnly")
            raw = r.headers.get("Set-Cookie","")
            if "SameSite" not in raw: issues.append("Missing SameSite")
            if issues:
                self.add_finding(f"Insecure Cookie: {cookie.name}", "MEDIUM",
                    "; ".join(issues), cookie.name)

    def scan_info_disclosure(self):
        print_status("Checking information disclosure...", "scan")
        error_urls = [f"{self.target}/nonexistent_{hashlib.md5(str(time.time()).encode()).hexdigest()[:8]}"]
        for url in error_urls:
            r = self.safe_get(url, timeout=5)
            if r:
                indicators = ["stack trace","traceback","exception","debug","at line",
                            "vendor/","node_modules/","internal server error"]
                for ind in indicators:
                    if ind in r.text.lower():
                        self.add_finding("Information Disclosure in Errors", "MEDIUM",
                            f"Error pages reveal internal info", ind)
                        break

    def scan_http_methods(self):
        print_status("Testing HTTP methods...", "scan")
        dangerous = ["PUT","DELETE","TRACE","CONNECT"]
        for method in dangerous:
            try:
                r = self.session.request(method, self.target, timeout=5)
                if r.status_code not in (405, 501, 403):
                    self.add_finding(f"Dangerous HTTP Method: {method}", "MEDIUM",
                        f"{method} returned {r.status_code}", method)
            except: pass

    # ─── REPORT GENERATION ──────────────────────────────────
    def generate_report(self):
        duration = (datetime.now() - self.start_time).total_seconds()
        counts = {"CRITICAL":0,"HIGH":0,"MEDIUM":0,"LOW":0,"INFO":0}
        for f in self.findings: counts[f["severity"]] = counts.get(f["severity"],0)+1
        report_lines = [
            "="*70, "  CLAN NXT - VULNERABILITY SCAN REPORT", "="*70,
            f"  Target:   {self.target}",
            f"  Date:     {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"  Duration: {duration:.1f} seconds",
            f"  Findings: {len(self.findings)} total", "",
            f"  CRITICAL: {counts['CRITICAL']}  |  HIGH: {counts['HIGH']}  |  MEDIUM: {counts['MEDIUM']}  |  LOW: {counts['LOW']}",
            "="*70, ""
        ]
        for f in self.findings:
            report_lines.extend([
                f"[{f['severity']}] {f['title']}",
                f"  Details:  {f['details']}",
                f"  Evidence: {f['evidence']}" if f['evidence'] else "",
                ""
            ])
        report_text = "\n".join(report_lines)
        filepath = save_report(f"vuln_scan_{self.parsed.hostname}", report_text)
        # Print summary
        print(f"\n{C.R}{'═'*65}{C.RST}")
        print(f"  {C.W}{C.BOLD}SCAN COMPLETE - VULNERABILITY REPORT{C.RST}")
        print(f"{C.R}{'═'*65}{C.RST}")
        print(f"  {C.GR}Target:{C.RST}   {C.W}{self.target}{C.RST}")
        print(f"  {C.GR}Duration:{C.RST} {C.W}{duration:.1f}s{C.RST}")
        print(f"  {C.GR}Findings:{C.RST} {C.W}{len(self.findings)}{C.RST}")
        print(f"\n  {C.R}CRITICAL: {counts['CRITICAL']}{C.RST}  {C.Y}HIGH: {counts['HIGH']}{C.RST}  {C.CY}MEDIUM: {counts['MEDIUM']}{C.RST}  {C.GR}LOW: {counts['LOW']}{C.RST}")
        print(f"\n  {C.G}Report saved: {C.W}{filepath}{C.RST}")
        print(f"{C.R}{'═'*65}{C.RST}")
        return filepath

    def run_full_scan(self):
        print_header("FULL VULNERABILITY SCAN", self.target)
        scans = [
            ("Security Headers", self.scan_security_headers),
            ("SSL/TLS Config", self.scan_ssl_tls),
            ("Directory Enumeration", self.scan_directory_enum),
            ("API Key Exposure", self.scan_api_keys),
            ("SQL Injection", self.scan_sql_injection),
            ("Cross-Site Scripting", self.scan_xss),
            ("CORS Misconfiguration", self.scan_cors),
            ("Rate Limiting", self.scan_rate_limiting),
            ("Open Redirects", self.scan_open_redirect),
            ("Clickjacking", self.scan_clickjacking),
            ("Cookie Security", self.scan_cookies),
            ("Information Disclosure", self.scan_info_disclosure),
            ("HTTP Methods", self.scan_http_methods),
        ]
        for i, (name, func) in enumerate(scans):
            print(f"\n  {C.R}[{i+1}/{len(scans)}]{C.RST} {C.W}{name}{C.RST}")
            try: func()
            except Exception as e: print_status(f"Error in {name}: {e}", "error")
        return self.generate_report()


def vuln_scanner_menu():
    """Main vulnerability scanner interface."""
    if not REQUESTS_OK:
        print_status("'requests' library required. Install: pip3 install requests", "error")
        return
    while True:
        clear_screen()
        print(f"\n{C.R}  ╔══════════════════════════════════════════════════╗{C.RST}")
        print(f"{C.R}  ║{C.RST}  {C.W}{C.BOLD}🛡 VULNERABILITY SCANNER{C.RST}                        {C.R}║{C.RST}")
        print(f"{C.R}  ╚══════════════════════════════════════════════════╝{C.RST}\n")
        print_menu_option("1","Full Scan","Complete vulnerability assessment")
        print_menu_option("2","Quick Scan","Headers, SSL, dirs only")
        print_menu_option("3","SQL Injection Test","Focused SQLi testing")
        print_menu_option("4","XSS Test","Focused XSS testing")
        print_menu_option("5","API Key Scan","Check for exposed secrets")
        print_menu_option("0","Back to Main Menu")
        ch = get_input("vuln-scanner")
        if ch in ("0","back","exit"): break
        if ch not in ("1","2","3","4","5"): continue
        url = input(f"\n  {C.CY}Target URL (https://example.com):{C.RST} ").strip()
        if not url.startswith("http"): url = "https://" + url
        if not is_valid_url(url):
            print_status("Invalid URL.","error"); get_input("enter"); continue
        if not confirm_action(f"Scan {url}? Ensure you have authorization."):
            continue
        import urllib3; urllib3.disable_warnings()
        scanner = VulnScanner(url)
        log_action("VULN_SCAN", url)
        if ch=="1": scanner.run_full_scan()
        elif ch=="2":
            scanner.scan_security_headers(); scanner.scan_ssl_tls()
            scanner.scan_directory_enum(); scanner.generate_report()
        elif ch=="3": scanner.scan_sql_injection(); scanner.generate_report()
        elif ch=="4": scanner.scan_xss(); scanner.generate_report()
        elif ch=="5": scanner.scan_api_keys(); scanner.generate_report()
        get_input("enter")

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sys

# Define payloads
SQLI_PAYLOADS = ["'", "\"", "' OR '1'='1", "\" OR \"1\"=\"1\" --"]
XSS_PAYLOADS = ["<script>alert('XSS')</script>", "<img src=x onerror=alert('XSS')>"]

# Known SQL error indicators
SQL_ERRORS = [
    "you have an error in your sql syntax",
    "warning: mysql",
    "quoted string not properly terminated",
    "unclosed quotation mark after the character string",
]

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 (scanner)"})

def get_forms(url):
    """Return all forms present on a web page."""
    resp = session.get(url)
    soup = BeautifulSoup(resp.content, "html.parser")
    return soup.find_all("form")

def get_form_details(form):
    """Extract action, method, and inputs from a form."""
    action = form.get("action") or ""
    method = form.get("method", "get").lower()
    inputs = []
    for inp in form.find_all("input"):
        inputs.append({
            "name": inp.get("name"),
            "type": inp.get("type", "text"),
            "value": inp.get("value", "")
        })
    return {"action": action, "method": method, "inputs": inputs}

def contains_sql_error(text):
    lower = text.lower()
    return any(err in lower for err in SQL_ERRORS)

def test_sqli(url):
    print(f"[*] SQLi testing: {url}")
    # URL injection
    for payload in SQLI_PAYLOADS:
        r = session.get(url + payload)
        if contains_sql_error(r.text):
            print(f"[!] SQLi likely at URL: {url + payload}")
            return True
    # Form injection
    for form in get_forms(url):
        d = get_form_details(form)
        target = urljoin(url, d["action"])
        for payload in SQLI_PAYLOADS:
            data = {}
            for inp in d["inputs"]:
                if inp["type"] in ["hidden", "submit"]:
                    data[inp["name"]] = inp["value"] + payload
                else:
                    data[inp["name"]] = payload
            r = session.post(target, data=data) if d["method"] == "post" else session.get(target, params=data)
            if contains_sql_error(r.text):
                print(f"[!] SQLi vulnerability in form at: {target}")
                return True
    print("[+] No SQLi detected.")
    return False

def test_xss(url):
    print(f"[*] XSS testing: {url}")
    for form in get_forms(url):
        d = get_form_details(form)
        target = urljoin(url, d["action"])
        for payload in XSS_PAYLOADS:
            data = {inp["name"]: payload for inp in d["inputs"] if inp["name"]}
            r = session.post(target, data=data) if d["method"] == "post" else session.get(target, params=data)
            if payload in r.text:
                print(f"[!] XSS vulnerability detected in form at: {target}")
                return True
    print("[+] No XSS detected.")
    return False

def scan(url):
    print(f"=== Scanning {url} ===\n")
    _ = test_sqli(url)
    _ = test_xss(url)
    print("\n=== Scan complete ===")

if _name_ == "_main_":
    if len(sys.argv) != 2:
        print("Usage: python vuln_scanner.py https://example.com/page")
        sys.exit(1)
    scan(sys.argv[1])
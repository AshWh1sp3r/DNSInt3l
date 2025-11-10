#!/usr/bin/env python3
"""
dnsint3l_enhanced.py
Lightweight recon helper (improved)
Author: AshWh1sp3r (enhanced)
Description:
    This tool performs lightweight DNS and hosting recon for a given domain
    using KeyCDN's public tools.geo page.
"""

import argparse
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import sys
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ==============================
# Global Session
# ==============================
SESSION = requests.Session()


# ==============================
# Retry configuration
# ==============================
def configure_retries(session, total=3, backoff_factor=1,
                      status_forcelist=(429, 500, 502, 503, 504)):
    """
    Configure HTTP retries for the session to handle transient errors.
    - total: number of retries
    - backoff_factor: delay multiplier between retries
    - status_forcelist: HTTP codes that trigger retry
    """
    retries = Retry(total=total, backoff_factor=backoff_factor, status_forcelist=status_forcelist)
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)


# ==============================
# Build headers
# ==============================
def build_headers(domain):
    """
    Build realistic HTTP headers for requests.
    - domain: used to set X-Origin header dynamically
    """
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Origin": "https://tools.keycdn.com",
        "Priority": "u=1, i",
        "Referer": "https://tools.keycdn.com/",
        "Sec-CH-UA": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
        "Sec-CH-UA-Mobile": "?0",
        "Sec-CH-UA-Platform": '"Linux"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/139.0.0.0 Safari/537.36",
        "X-Client": "carbon.js/20231113 (serveUrl:CK7D52QN;serve:CK7D52QN)",
        "X-Origin": f"https://tools.keycdn.com/geo?host={domain}"
    }
    return headers


# ==============================
# Tor Proxy
# ==============================
def tor_proxies():
    """
    Return proxy configuration for local Tor.
    Requires Tor service running on 127.0.0.1:9050
    """
    return {
        "http": "socks5h://127.0.0.1:9050",
        "https": "socks5h://127.0.0.1:9050"
    }


# ==============================
# Normalize domain
# ==============================
def normalize_domain(domain: str) -> str:
    """
    Clean user input into a domain / host.
    - Removes URL schemes (http://, https://)
    - Removes trailing slashes
    - Keeps only the hostname if user passed a full URL with path
    """
    # Remove leading/trailing spaces
    d = domain.strip()

    # Remove scheme if present
    if d.startswith("http://"):
        d = d[len("http://"):]
    elif d.startswith("https://"):
        d = d[len("https://"):]

    # Remove trailing slashes
    d = d.rstrip("/")

    # If user included path, keep only the hostname
    if "/" in d:
        d = d.split("/")[0]

    return d


# ==============================
# Save results
# ==============================
def save_results(base_name: str, text: str, data_lines: list):
    """
    Save output to a timestamped text file.
    - base_name: filename base
    - text: header or main text
    - data_lines: lines of data to append
    Returns the saved file path.
    """
    ts = datetime.now().strftime("%Y%m%dT%H%M%SZ")
    filename = f"{base_name}_{ts}.txt"
    with open(filename, "w", encoding="utf-8") as fh:
        fh.write(f"{text}\n\n")
        for line in data_lines:
            fh.write(f"{line}\n")
    return filename


# ==============================
# Parse KeyCDN geo HTML
# ==============================
def parse_keycdn_geo(html: str):
    """
    Parse KeyCDN's tools.geo page:
    - dt tags = label
    - dd tags = value
    Returns a list of (label, value) tuples.
    """
    soup = BeautifulSoup(html, "html.parser")
    dts = [el.text.strip() for el in soup.find_all("dt")]
    dds = [el.text.strip() for el in soup.find_all("dd")]

    # Pair labels and values (avoid IndexError if unequal length)
    pairs = []
    n = min(len(dts), len(dds))
    for i in range(n):
        pairs.append((dts[i], dds[i]))
    return pairs


# ==============================
# Main program
# ==============================
def main():
    # Command-line arguments
    parser = argparse.ArgumentParser(description="dnsint3l - lightweight recon helper (KeyCDN-backed)")
    parser.add_argument("domain", help="Domain to recon (e.g., example.com)")
    parser.add_argument("--tor", action="store_true", help="Route requests through local Tor")
    parser.add_argument("--out", default="Dns_Intel_Results", help="Output filename base (timestamp appended)")
    parser.add_argument("--timeout", type=int, default=15, help="Request timeout in seconds")
    args = parser.parse_args()

    # Clean the domain input
    domain = normalize_domain(args.domain)
    if not domain:
        print("Invalid domain. Exiting.")
        sys.exit(1)

    # Configure session retries
    configure_retries(SESSION)

    # Build headers and proxies
    headers = build_headers(domain)
    proxies = tor_proxies() if args.tor else None

    # Perform GET request to KeyCDN geo page
    url = f"https://tools.keycdn.com/geo?host={domain}"
    try:
        resp = SESSION.get(url, headers=headers, proxies=proxies,
                           timeout=(args.timeout, args.timeout))
        resp.raise_for_status()  # Raise error for bad HTTP status
    except requests.exceptions.RequestException as e:
        print("Network error or request failed:", e)
        return

    print("Page loaded successfully!\n")

    # Parse results
    pairs = parse_keycdn_geo(resp.text)
    if not pairs:
        print("Could not find the required data on the page.")
        return

    # Print results
    print(f"Querying {domain}....")
    print("Location & Network Details:\n")

    lines = []
    for label, value in pairs:
        line = f"{label} --------------------- {value}"
        print(line)
        lines.append(line)

    # Add header and separator for saving
    separator = "-" * 80
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header_text = f"DNS Intel Results for {domain}:\nQueried on: {now}\n{separator}"
    lines_with_header = [header_text] + lines + [separator]

    # Save results to file
    out_path = save_results(args.out, "\n".join(lines_with_header), [])
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()    proxies = {
        'http': 'socks5h://127.0.0.1:9050',
        'https': 'socks5h://127.0.0.1:9050'
    }
    return proxies

def retry():
    """Configure retries for the session."""
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 501, 502, 503]
    )
    adapter = HTTPAdapter(max_retries=retries)
    s.mount('http://', adapter)
    s.mount('https://', adapter)

def main():
    retry()
    proxies = use_tor()
    headers = get_useragent()
    domain = input("Enter the domain you want to perform recon on (eg., example.com): ")
    if domain.startswith(("https://", "http://")) and domain.endswith('/'):
        domain.replace("https://", "")
        domain.replace("http://", "")
        domain.strip('/')

    url = f"https://tools.keycdn.com/geo?host={domain}"

    try:
        # Step 1 — get the main page
        resp = s.get(url, proxies=proxies, headers=headers, timeout=(10, 10))
        resp.encoding = 'utf-8'

        if resp.status_code != 200:
            print("Initial GET failed:", resp.status_code)
            return

        print("Page loaded successfully!\n")
        soup = BeautifulSoup(resp.text, "html.parser")
        dd = soup.find_all('dd')
        dt = soup.find_all('dt')
        if dd and dt:
            print(f"Querying {domain}....")
            print("Location & Network Details:\n")
            len_dd = len(dd)
            for i in range(len_dd):
                print(f"{dt[i].text.strip()} --------------------- {dd[i].text.strip()}")
            seperator = "-" * 120
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open("Dns_Intel_Results.txt", "a") as f:
                f.write(f"\nDNS Intel Results for {domain}:\n")
                f.write(f"Queried on: {now}\n")
                for i in range(len_dd):
                    f.write(f"{dt[i].text.strip()} --------------------- {dd[i].text.strip()}\n")
                    f.write(f"{seperator}\n")
            print(f"\nResults saved to Dns_Intel_Results.txt")
        else:
            print("Could not find the required data on the page.")
    except requests.exceptions.RequestException as e:
        print("Network error:", e)

if __name__ == "__main__":
    main()

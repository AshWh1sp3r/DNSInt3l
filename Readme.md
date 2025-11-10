# DNSInt3l Enhanced

**Lightweight DNS and hosting recon helper (KeyCDN-backed)**  
Author: AshWh1sp3r (enhanced)

---

## Description

`DNSInt3l Enhanced` is a Python-based recon tool designed to gather DNS and hosting information for any domain using KeyCDN’s public tools. It’s lightweight, reliable, and allows optional Tor routing for anonymity.

The tool fetches details such as:

- IP address
- Hostname
- Provider / ASN
- Location (Country, Continent, Coordinates)
- Query timestamp  

All results are formatted and saved into a timestamped file for easy reference.

---

## Features

- Simple command-line interface
- Optional Tor proxy support
- Configurable request timeout
- Automatic retries on network failures
- Outputs results to both terminal and file
- Beautifully formatted, human-readable output

---

## Requirements

- Python 3.8+
- Python packages:
  ```bash
  pip install requests beautifulsoup4

Optional: Tor running locally on 127.0.0.1:9050 for --tor option



---

Usage

python3 dnsint3l_enhanced.py DOMAIN [options]

Arguments:

Argument	Description

DOMAIN	The domain to perform recon on (e.g., example.com)


Options:

Option	Description

--tor	Route requests through local Tor (socks5h://127.0.0.1:9050)
--out <filename>	Base name for output file (timestamp will be appended). Default: Dns_Intel_Results
--timeout <seconds>	Request timeout in seconds. Default: 15


Example Commands:

Basic recon:


python3 dnsint3l_enhanced.py example.com

Using Tor and custom output file:


python3 dnsint3l_enhanced.py example.com --tor --out MyDNSResults

Custom timeout:


python3 dnsint3l_enhanced.py example.com --timeout 20


---

Output

Results are printed in the terminal and saved in a file like:

Dns_Intel_Results_20251110T195430Z.txt

Example format:

DNS Intel Results for example.com
Queried on: 2025-11-10 19:54:30
--------------------------------------------------------------------------------
Country --------------------- United States (US)
Continent --------------------- North America (NA)
Coordinates --------------------- 37.751 / -97.822
IP address --------------------- 142.250.74.206
Hostname --------------------- fra24s02-in-f14.1e100.net
Provider --------------------- GOOGLE
ASN --------------------- 15169
--------------------------------------------------------------------------------


---

Notes

Ensure your network allows access to https://tools.keycdn.com/geo.

Use Tor only if it is properly installed and running locally.

The script does not scrape any private or sensitive information; it relies solely on KeyCDN’s public pages.



---

License

This project is for educational and ethical purposes only. Unauthorized use against targets without consent is strictly prohibited.

---


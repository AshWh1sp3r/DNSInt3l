import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from urllib3.util import Retry
from requests.adapters import HTTPAdapter
from datetime import datetime


# ==============================
#  Tool Name: DNSInt3l
#  Author: AshWh1sp3r
#  Description: A lightweight recon tool to fetch hosting and DNS intel
#               for a given domain using KeyCDN's public data page.
#  Version: 1.0
# ==============================


# Create a session
s = requests.Session()

def get_useragent():
    """Generate a random or fallback user-agent."""
    try:
        ua = UserAgent()
        headers = {'User-Agent': ua.random}
    except Exception:
        headers = {
            'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/58.0.3029.110 Safari/537.3')
        }
    s.headers.update(headers)
    return headers

def use_tor():
    """Return TOR proxy configuration."""
    proxies = {
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

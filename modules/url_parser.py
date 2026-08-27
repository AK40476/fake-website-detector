from urllib.parse import urlparse
import re

def parse_url(url):
    # Add http if missing
    if not url.startswith(("http://", "https://")):
        url = "http://" + url

    parsed = urlparse(url)

    domain = parsed.hostname
    protocol = parsed.scheme
    path = parsed.path

    # Check if IP-based URL
    ip_pattern = r"^\d{1,3}(\.\d{1,3}){3}$"
    is_ip = bool(re.match(ip_pattern, domain)) if domain else False

    # Count subdomains
    subdomain_count = 0
    if domain and not is_ip:
        parts = domain.split(".")
        if len(parts) > 2:
            subdomain_count = len(parts) - 2

    return {
        "original_url": url,
        "protocol": protocol,
        "domain": domain,
        "path": path,
        "is_ip": is_ip,
        "subdomain_count": subdomain_count
    }

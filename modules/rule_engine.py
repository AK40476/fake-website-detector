import os
import re
from urllib.parse import urlparse

from modules.security_check import check_ssl_certificate
from modules.scoring import get_risk_level

def calculate_risk(url):
    score = 0
    reasons = []

    parsed = urlparse(url)
    domain = parsed.netloc.split(":")[0]
    path = parsed.path

    # 1. HTTP instead of HTTPS
    if parsed.scheme != "https":
        score += 25
        reasons.append("Website is not using HTTPS")

    # 2. SSL Certificate Validation
    if parsed.scheme == "https":
        ssl_valid, ssl_message = check_ssl_certificate(domain)
    
        if not ssl_valid:
            score += 30
            reasons.append(ssl_message)

    # 3. IP Address instead of domain
    ip_pattern = r"^\d{1,3}(\.\d{1,3}){3}$"
    if re.match(ip_pattern, domain):
        score += 30
        reasons.append("Uses IP address instead of domain name")

    # 4. Long URL
    if len(url) > 75:
        score += 20
        reasons.append("URL length is suspiciously long")

    # 5. Too many subdomains
    subdomains = domain.split(".")
    if len(subdomains) > 3:
        score += 25
        reasons.append("Too many subdomains")

    # 6. Suspicious keywords
    suspicious_keywords = ["login", "verify", "update", "secure", "account", "bank"]
    for keyword in suspicious_keywords:
        if keyword in url.lower():
            score += 20
            reasons.append(f"Contains suspicious keyword: {keyword}")

    # 7. Hyphen abuse detection
    hyphen_count = domain.count('-')
    if hyphen_count >= 2:
        score += 20
        reasons.append("Domain contains multiple hyphens (common phishing trick)")

    # 8. @ symbol trick
    if "@" in url:
        score += 30
        reasons.append("URL contains '@' symbol (possible redirection trick)")

    # 9. Brand impersonation detection
    brands = load_brands()

    for brand in brands:
        if brand in domain and brand not in domain.split(".")[0]:
            score += 25
            reasons.append(f"Possible brand impersonation: {brand}")

    # 10. Suspicious TLD detection
    suspicious_tlds = load_suspicious_tlds()
    domain_parts = domain.split(".")
    
    if len(domain_parts) > 1:
        tld = domain_parts[-1].lower()
        if tld in suspicious_tlds:
            score += 25
            reasons.append(f"Suspicious top-level domain: .{tld}")        
    
    # 11. URL Shortener Detection
    shorteners = [
        "bit.ly",
        "tinyurl.com",
        "t.co",
        "goo.gl",
        "ow.ly"
    ]

    for short in shorteners:
        if short in url.lower():
            score += 25
            reasons.append("URL uses link shortening service")
    
    # 12. Excessive digits in domain
    digit_count = sum(c.isdigit() for c in domain)

    if digit_count >= 4:
        score += 15
        reasons.append("Domain contains excessive numbers")

    # 13. Repeated character detection
    if re.search(r"(.)\1{2,}", domain):
        score += 20
        reasons.append("Domain contains repeated characters")

    # 14. Dangerous file extension
    dangerous_ext = [".exe", ".zip", ".scr", ".apk"]

    for ext in dangerous_ext:
        if url.lower().endswith(ext):
            score += 40
            reasons.append("URL may trigger a malicious file download")

    # 15. Fake subdomain brand attack
    for brand in brands:
        if brand in url.lower() and not domain.startswith(brand):
            score += 30
            reasons.append(f"Brand name '{brand}' used in misleading subdomain")
            break        
    
    # 16. Suspicious 'www' usage
    if "www-" in domain or "www." not in url[:12]:
        score += 10
        reasons.append("Suspicious usage of 'www' in domain")

    # 17. Double slash redirect
    if "//" in path:
        score += 20
        reasons.append("URL contains double slash redirect pattern")

    # Normalize score
    score = max(0, min(score, 100))

    level = get_risk_level(score)
    return score, level, reasons      

def load_brands():
    path = os.path.join(os.getcwd(), "data", "brand_names.txt")
    try:
        with open(path, "r") as file:
            return [line.strip() for line in file if line.strip()]
    except:
        return []

def load_suspicious_tlds():
    path = os.path.join(os.getcwd(), "data", "suspicious_tlds.txt")
    try:
        with open(path, "r") as file:
            return [line.strip() for line in file if line.strip()]
    except:
        return []
    
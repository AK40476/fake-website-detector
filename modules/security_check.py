import ssl
import socket
from datetime import datetime

def check_ssl_certificate(domain):
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                
                expiry_date = datetime.strptime(cert['notAfter'], "%b %d %H:%M:%S %Y %Z")
                
                if expiry_date < datetime.utcnow():
                    return False, "SSL certificate is expired"
                
                return True, "SSL certificate is valid"
    except Exception:
        return False, "SSL certificate is invalid or cannot be verified"

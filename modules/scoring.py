def get_risk_level(score):
    if score >= 60:
        return "High Risk (Likely Phishing)"
    elif score >= 30:
        return "Suspicious"
    else:
        return "Safe"
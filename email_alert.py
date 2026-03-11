# =====================================================
# EMAIL ALERT SYSTEM (100% CLEAN VERSION)
# =====================================================

import smtplib
from email.mime.text import MIMEText

# 👉 CHANGE THIS ONLY
SENDER = "managercryptoportfolio@gmail.com"
APP_PASSWORD = "ajlu qjxx absa heei"


# ---------------- REGISTRATION MAIL ----------------
def send_registration_mail(username):

    try:

        body = f"""
Hello {username},

Welcome to Crypto Portfolio Manager 🚀

Your registration was successful.

Regards,
Crypto Portfolio Manager
"""

        msg = MIMEText(body)
        msg["Subject"] = "Registration Successful"
        msg["From"] = SENDER
        msg["To"] = SENDER

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER, APP_PASSWORD)
            server.send_message(msg)

    except Exception as e:
        print("Registration mail failed:", e)


# ---------------- RISK ALERT ----------------
def send_alert(df):

    try:

        body = f"""
⚠ HIGH RISK ALERT

{df.to_string()}
"""

        msg = MIMEText(body)
        msg["Subject"] = "Crypto Risk Alert"
        msg["From"] = SENDER
        msg["To"] = SENDER

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER, APP_PASSWORD)
            server.send_message(msg)

    except Exception as e:
        print("Risk mail failed:", e)

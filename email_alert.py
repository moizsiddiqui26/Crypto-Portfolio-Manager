# =====================================================
# EMAIL ALERT SYSTEM (FINAL FIXED VERSION)
# =====================================================

import smtplib
from email.mime.text import MIMEText

SENDER = "managercryptoportfolio@gmail.com"
APP_PASSWORD = "ajlu qjxx absa heei"   # 👉 add Gmail App Password


# ---------------- REGISTRATION MAIL ----------------
def send_registration_mail(name, user_email):

    try:

        body = f"""
Hello {name},

Welcome to Crypto Portfolio Manager 🚀

Your registration was successful.

You can now log in and start managing your investments.

Regards,
Crypto Portfolio Manager
"""

        msg = MIMEText(body)
        msg["Subject"] = "Registration Successful"
        msg["From"] = SENDER
        msg["To"] = user_email

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER, APP_PASSWORD)
            server.send_message(msg)

    except Exception as e:
        print("Registration mail failed:", e)

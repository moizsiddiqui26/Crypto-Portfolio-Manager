# =====================================================
# EMAIL ALERT SYSTEM - FINAL VERSION
# =====================================================

import smtplib
from email.mime.text import MIMEText

# ---------------- CONFIG ----------------
SENDER="managercryptoportfolio@gmail.com"
APP_PASSWORD="YOUR_APP_PASSWORD"   # 🔥 PUT APP PASSWORD HERE


# =====================================================
# REGISTRATION MAIL
# =====================================================
def send_registration_mail(username):

    body=f"""
Welcome to Crypto Portfolio Manager 🚀

Hello {username},

Your registration was successful.

You can now log in and start managing your crypto investments.

Regards,
Crypto Portfolio Manager
"""

    msg=MIMEText(body)
    msg["Subject"]="Registration Successful"
    msg["From"]=SENDER
    msg["To"]=SENDER   # sending to same mail

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com",465) as server:
            server.login(SENDER,APP_PASSWORD)
            server.send_message(msg)
    except:
        print("Mail failed")


# =====================================================
# RISK ALERT MAIL
# =====================================================
def send_alert(df):

    body=f"""
⚠ HIGH RISK ALERT

Some cryptocurrencies show high volatility.

Details:

{df.to_string()}

Check dashboard for updates.
"""

    msg=MIMEText(body)
    msg["Subject"]="Crypto Risk Alert"
    msg["From"]=SENDER
    msg["To"]=SENDER

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com",465) as server:
            server.login(SENDER,APP_PASSWORD)
            server.send_message(msg)
    except:
        print("Alert mail failed")

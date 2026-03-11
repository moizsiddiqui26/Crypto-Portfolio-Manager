# =====================================================
# EMAIL ALERT SYSTEM (FINAL WORKING VERSION)
# =====================================================

import smtplib
from email.mime.text import MIMEText

SENDER="managercryptoportfolio@gmail.com"
APP_PASSWORD="YOUR_APP_PASSWORD"   # 🔥 PUT YOUR APP PASSWORD


# =====================================================
# REGISTRATION MAIL
# =====================================================
def send_registration_mail(user_email):

    body=f"""
🎉 Welcome to Crypto Portfolio Manager!

Hello {user_email},

Your registration was successful.

You can now:

✔ Track investments  
✔ View analytics  
✔ Check risk levels  
✔ Predict profits  

Start managing your crypto today 🚀

Regards,
Crypto Portfolio Manager
"""

    msg=MIMEText(body)
    msg["Subject"]="Registration Successful"
    msg["From"]=SENDER
    msg["To"]=user_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com",465) as server:
            server.login(SENDER,APP_PASSWORD)
            server.send_message(msg)

        print("Registration mail sent")

    except Exception as e:
        print("Registration mail failed:",e)


# =====================================================
# RISK ALERT MAIL
# =====================================================
def send_alert(df,user_email):

    body=f"""
⚠ CRYPTO RISK ALERT

High volatility detected in your portfolio.

Details:

{df.to_string()}

Check dashboard immediately.

Stay alert 🚨
"""

    msg=MIMEText(body)
    msg["Subject"]="Crypto Risk Alert"
    msg["From"]=SENDER
    msg["To"]=user_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com",465) as server:
            server.login(SENDER,APP_PASSWORD)
            server.send_message(msg)

        print("Risk mail sent")

    except Exception as e:
        print("Risk mail failed:",e)

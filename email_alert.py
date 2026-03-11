import smtplib
from email.mime.text import MIMEText

# EMAIL CONFIG 
SENDER="managercryptoportfolio@gmail.com"
APP_PASSWORD="ajlu qjxx absa heei" 

# REGISTRATION MAIL
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
    msg["To"]=SENDER   )

    with smtplib.SMTP_SSL("smtp.gmail.com",465) as server:
        server.login(SENDER,APP_PASSWORD)
        server.send_message(msg)



# RISK ALERT MAIL
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

    with smtplib.SMTP_SSL("smtp.gmail.com",465) as server:
        server.login(SENDER,APP_PASSWORD)
        server.send_message(msg)

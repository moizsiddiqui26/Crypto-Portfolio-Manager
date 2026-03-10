import smtplib
from email.mime.text import MIMEText

SENDER="managercryptoportfolio@gmail.com"
APP_PASS="ajlu qjxx absa heei"

def send_registration_mail(user,name):

    msg=MIMEText(f"Hello {name}, Registration Successful.")
    msg["Subject"]="Registration Success"
    msg["From"]=SENDER
    msg["To"]=user

    with smtplib.SMTP_SSL("smtp.gmail.com",465) as s:
        s.login(SENDER,APP_PASS)
        s.send_message(msg)

def send_alert(df):

    msg=MIMEText(f"High Risk Alert:\n{df}")
    msg["Subject"]="Crypto Risk Alert"
    msg["From"]=SENDER
    msg["To"]=SENDER

    with smtplib.SMTP_SSL("smtp.gmail.com",465) as s:
        s.login(SENDER,APP_PASS)
        s.send_message(msg)

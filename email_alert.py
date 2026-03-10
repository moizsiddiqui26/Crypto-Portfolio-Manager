import smtplib
from email.mime.text import MIMEText

SENDER="managercryptoportfolio@gmail.com"
APP_PASS="PUT_APP_PASSWORD"

def send_registration_mail(email,name):

    msg=MIMEText(f"Hello {name}, Registration successful.")
    msg["Subject"]="Welcome"
    msg["From"]=SENDER
    msg["To"]=email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com",465) as s:
            s.login(SENDER,APP_PASS)
            s.send_message(msg)
    except Exception as e:
        print("Email error:",e)

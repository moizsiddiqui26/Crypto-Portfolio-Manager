import smtplib
from email.mime.text import MIMEText

SENDER="managercryptoportfolio@gmail.com"
APP_PASSWORD="ajlu qjxx absa heei"

def send_registration_mail(email):
    msg=MIMEText("Registration successful")
    msg["Subject"]="Welcome"
    msg["From"]=SENDER
    msg["To"]=email
    with smtplib.SMTP_SSL("smtp.gmail.com",465) as s:
        s.login(SENDER,APP_PASSWORD)
        s.send_message(msg)

def send_otp_mail(email,otp):
    msg=MIMEText(f"Your OTP is {otp}")
    msg["Subject"]="OTP"
    msg["From"]=SENDER
    msg["To"]=email
    with smtplib.SMTP_SSL("smtp.gmail.com",465) as s:
        s.login(SENDER,APP_PASSWORD)
        s.send_message(msg)

def send_alert(df,email):
    msg=MIMEText(df.to_string())
    msg["Subject"]="Risk Alert"
    msg["From"]=SENDER
    msg["To"]=email
    with smtplib.SMTP_SSL("smtp.gmail.com",465) as s:
        s.login(SENDER,APP_PASSWORD)
        s.send_message(msg)

import smtplib
from email.mime.text import MIMEText

SENDER="managercryptoportfolio@gmail.com"
APP_PASSWORD="Manager@123"

def send_alert(df):

    body=f"""
High Risk Alert!

{df.to_string()}
"""

    msg=MIMEText(body)
    msg["Subject"]="Crypto Risk Alert"
    msg["From"]=SENDER
    msg["To"]=SENDER

    with smtplib.SMTP_SSL("smtp.gmail.com",465) as server:
        server.login(SENDER,APP_PASSWORD)
        server.send_message(msg)

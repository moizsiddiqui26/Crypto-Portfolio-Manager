import streamlit as st
import json,os,random
from email_alert import send_registration_mail,send_otp_mail

st.set_page_config(page_title="Crypto Portfolio Manager",layout="wide")

USER_DB="users.json"

def load_users():
    if not os.path.exists(USER_DB): return {}
    try:
        with open(USER_DB,"r") as f: return json.load(f)
    except: return {}

def save_users(users):
    with open(USER_DB,"w") as f: json.dump(users,f)

if "auth" not in st.session_state: st.session_state.auth=False
if "mode" not in st.session_state: st.session_state.mode="login"
if "otp" not in st.session_state: st.session_state.otp=None
if "reset_user" not in st.session_state: st.session_state.reset_user=None

def login_ui():

    st.title("🚀 Crypto Portfolio Manager")
    users=load_users()

    if st.session_state.mode=="login":

        with st.form("login"):
            email=st.text_input("Email")
            pwd=st.text_input("Password",type="password")

            if st.form_submit_button("Login"):
                if email in users and users[email]["password"]==pwd:
                    st.session_state.auth=True
                    st.session_state.email=email
                    st.rerun()
                else: st.error("Invalid login")

        col1,col2=st.columns(2)
        with col1:
            if st.button("Login with OTP"): st.session_state.mode="otp"
        with col2:
            if st.button("Forgot Password"): st.session_state.mode="forgot"

        if st.button("Register"): st.session_state.mode="register"

    elif st.session_state.mode=="register":

        with st.form("reg"):
            name=st.text_input("Name")
            email=st.text_input("Email")
            pwd=st.text_input("Password",type="password")

            if st.form_submit_button("Register"):
                if email not in users:
                    users[email]={"name":name,"password":pwd}
                    save_users(users)
                    send_registration_mail(email)
                    st.success("Registered")
                    st.session_state.mode="login"
                    st.rerun()
                else: st.error("User exists")

        if st.button("Back"): st.session_state.mode="login"

    elif st.session_state.mode=="otp":

        email=st.text_input("Email")

        if st.button("Send OTP"):
            if email in users:
                otp=str(random.randint(100000,999999))
                st.session_state.otp=otp
                st.session_state.reset_user=email
                send_otp_mail(email,otp)
                st.success("OTP sent")

        otp_input=st.text_input("Enter OTP")

        if st.button("Verify OTP"):
            if otp_input==st.session_state.otp:
                st.session_state.auth=True
                st.session_state.email=st.session_state.reset_user
                st.rerun()
            else: st.error("Wrong OTP")

    elif st.session_state.mode=="forgot":

        email=st.text_input("Email")

        if st.button("Send Reset OTP"):
            if email in users:
                otp=str(random.randint(100000,999999))
                st.session_state.otp=otp
                st.session_state.reset_user=email
                send_otp_mail(email,otp)
                st.success("OTP sent")

        otp_input=st.text_input("OTP")
        new_pass=st.text_input("New Password",type="password")

        if st.button("Reset Password"):
            if otp_input==st.session_state.otp:
                users[email]["password"]=new_pass
                save_users(users)
                st.success("Password Updated")
                st.session_state.mode="login"
                st.rerun()

if not st.session_state.auth:
    login_ui()
else:
    import dashboard
    dashboard.main()

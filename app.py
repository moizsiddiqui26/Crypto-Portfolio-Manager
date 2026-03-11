# =====================================================
# CRYPTO PORTFOLIO MANAGER - FINAL APP (OTP VERSION)
# =====================================================

import streamlit as st
import json,os,random
from email_alert import send_registration_mail,send_otp_mail

st.set_page_config(page_title="Crypto Portfolio Manager",layout="wide")

USER_DB="users.json"

# =====================================================
# LOAD USERS
# =====================================================
def load_users():
    if not os.path.exists(USER_DB):
        return {}
    try:
        with open(USER_DB,"r") as f:
            return json.load(f)
    except:
        return {}

# =====================================================
# SAVE USERS
# =====================================================
def save_users(users):
    with open(USER_DB,"w") as f:
        json.dump(users,f)

# =====================================================
# SESSION STATE
# =====================================================
if "auth" not in st.session_state: st.session_state.auth=False
if "mode" not in st.session_state: st.session_state.mode="login"
if "otp" not in st.session_state: st.session_state.otp=None
if "reset_user" not in st.session_state: st.session_state.reset_user=None


# =====================================================
# LOGIN UI
# =====================================================
def login_ui():

    st.title("🚀 Crypto Portfolio Manager")

    users=load_users()

# ================= LOGIN =================
    if st.session_state.mode=="login":

        with st.form("login_form"):

            email=st.text_input("Email")
            pwd=st.text_input("Password",type="password")

            if st.form_submit_button("Login"):

                if email in users and users[email]["password"]==pwd:

                    st.session_state.auth=True
                    st.session_state.user=email
                    st.session_state.email=email
                    st.rerun()

                else:
                    st.error("Invalid login")

        col1,col2=st.columns(2)

        with col1:
            if st.button("Login with OTP"):
                st.session_state.mode="otp"

        with col2:
            if st.button("Forgot Password"):
                st.session_state.mode="forgot"

# ================= REGISTER =================
    elif st.session_state.mode=="register":

        with st.form("reg_form"):

            name=st.text_input("Full Name")
            email=st.text_input("Email")
            pwd=st.text_input("Password",type="password")

            if st.form_submit_button("Register"):

                if email not in users:

                    users[email]={"name":name,"password":pwd}
                    save_users(users)

                    send_registration_mail(email)

                    st.success("Registered Successfully")
                    st.session_state.mode="login"
                    st.rerun()

                else:
                    st.error("User exists")

        if st.button("Back"):
            st.session_state.mode="login"

# ================= OTP LOGIN =================
    elif st.session_state.mode=="otp":

        email=st.text_input("Enter Email")

        if st.button("Send OTP"):

            if email in users:

                otp=str(random.randint(100000,999999))
                st.session_state.otp=otp
                st.session_state.reset_user=email

                send_otp_mail(email,otp)

                st.success("OTP sent")

            else:
                st.error("Email not registered")

        otp_input=st.text_input("Enter OTP")

        if st.button("Verify OTP"):

            if otp_input==st.session_state.otp:

                st.session_state.auth=True
                st.session_state.user=st.session_state.reset_user
                st.session_state.email=st.session_state.reset_user
                st.rerun()

            else:
                st.error("Wrong OTP")

        if st.button("Back"):
            st.session_state.mode="login"

# ================= FORGOT PASSWORD =================
    elif st.session_state.mode=="forgot":

        email=st.text_input("Enter Email")

        if st.button("Send Reset OTP"):

            if email in users:

                otp=str(random.randint(100000,999999))
                st.session_state.otp=otp
                st.session_state.reset_user=email

                send_otp_mail(email,otp)

                st.success("OTP sent")

            else:
                st.error("Email not found")

        otp_input=st.text_input("Enter OTP")
        new_pass=st.text_input("New Password",type="password")

        if st.button("Reset Password"):

            if otp_input==st.session_state.otp:

                users[email]["password"]=new_pass
                save_users(users)

                st.success("Password Updated")
                st.session_state.mode="login"
                st.rerun()

            else:
                st.error("Wrong OTP")


# =====================================================
# PROFILE EDIT
# =====================================================
def profile_edit():

    st.subheader("✏ Edit Profile")

    users=load_users()
    email=st.session_state.email

    name=st.text_input("Name",users[email]["name"])
    new_pass=st.text_input("New Password",type="password")

    if st.button("Update Profile"):

        users[email]["name"]=name

        if new_pass:
            users[email]["password"]=new_pass

        save_users(users)

        st.success("Profile Updated")


# =====================================================
# MAIN FLOW
# =====================================================
if not st.session_state.auth:

    login_ui()

else:

    col1,col2=st.columns([6,1])

    with col1:
        st.write(f"👋 Welcome **{st.session_state.user}**")

    with col2:
        if st.button("Logout"):
            st.session_state.auth=False
            st.rerun()

    st.divider()

    profile_edit()

    st.divider()

    import dashboard
    dashboard.main()

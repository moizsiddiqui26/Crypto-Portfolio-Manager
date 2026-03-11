# =====================================================
# CRYPTO PORTFOLIO MANAGER - FINAL APP
# =====================================================

import streamlit as st
import json,os
from email_alert import send_registration_mail

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Crypto Portfolio Manager",layout="wide")

USER_DB="users.json"

# ---------------- LOAD USERS ----------------
def load_users():
    if not os.path.exists(USER_DB):
        return {}
    try:
        with open(USER_DB,"r") as f:
            return json.load(f)
    except:
        return {}

# ---------------- SAVE USER ----------------
def save_user(name,u,p):
    users=load_users()
    if u in users:
        return False
    users[u]={"name":name,"password":p}
    with open(USER_DB,"w") as f:
        json.dump(users,f)

    # send mail
    send_registration_mail(u)

    return True


# ---------------- SESSION STATE ----------------
if "auth" not in st.session_state:
    st.session_state.auth=False

if "mode" not in st.session_state:
    st.session_state.mode="login"


# =====================================================
# AUTH UI
# =====================================================
def auth_ui():

    st.title("🚀 Crypto Portfolio Manager")

    # LOGIN
    if st.session_state.mode=="login":

        with st.form("login"):
            u=st.text_input("Username")
            p=st.text_input("Password",type="password")

            if st.form_submit_button("Login"):

                users=load_users()

                if u in users and users[u]["password"]==p:
                    st.session_state.auth=True
                    st.session_state.user=u
                    st.session_state.email=u
                    st.rerun()
                else:
                    st.error("Invalid Username or Password")

        if st.button("Register"):
            st.session_state.mode="register"
            st.rerun()

    # REGISTER
    else:

        with st.form("register"):
            name=st.text_input("Full Name")
            u=st.text_input("Username")
            p=st.text_input("Password",type="password")

            if st.form_submit_button("Register"):

                if save_user(name,u,p):
                    st.success("Registration Successful")
                    st.session_state.mode="login"
                    st.rerun()
                else:
                    st.error("Username already exists")

        if st.button("Back to Login"):
            st.session_state.mode="login"
            st.rerun()


# =====================================================
# MAIN FLOW
# =====================================================
if not st.session_state.auth:

    auth_ui()

else:

    col1,col2=st.columns([6,1])

    with col1:
        st.write(f"👋 Welcome **{st.session_state.user}**")

    with col2:
        if st.button("Logout"):
            st.session_state.auth=False
            st.rerun()

    st.divider()

    import dashboard
    dashboard.main()


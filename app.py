# =====================================================
# CRYPTO INVESTMENT MANAGER - FINAL APP
# =====================================================

import streamlit as st
import json
import os
from email_alert import send_registration_mail from email_alert
# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Crypto Investment Manager",layout="wide")

USER_DB="users.json"

# ---------------- LOAD USERS ----------------
def load_users():
    if not os.path.exists(USER_DB):
        return {}
    with open(USER_DB,"r") as f:
        return json.load(f)

# ---------------- SAVE USER ----------------
def save_user(name,email,password):
    users=load_users()
    if email in users:
        return False
    users[email]={"name":name,"password":password}
    with open(USER_DB,"w") as f:
        json.dump(users,f)
    return True

# ---------------- SESSION STATE ----------------
if "auth" not in st.session_state:
    st.session_state.auth=False

# =====================================================
# LOGIN + REGISTER UI
# =====================================================
if not st.session_state.auth:

    st.title("🚀 Crypto Investment Manager")

    tab1,tab2=st.tabs(["🔐 Login","📝 Register"])

    # ---------------- LOGIN ----------------
    with tab1:

        email_login=st.text_input("Email",key="login_email")
        pwd_login=st.text_input("Password",type="password",key="login_pwd")

        if st.button("Login",key="login_btn"):

            users=load_users()

            if email_login in users and users[email_login]["password"]==pwd_login:
                st.session_state.auth=True
                st.session_state.user=email_login
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid credentials")

    # ---------------- REGISTER ----------------
    with tab2:

        name_reg=st.text_input("Name",key="reg_name")
        email_reg=st.text_input("Email",key="reg_email")
        pwd_reg=st.text_input("Password",type="password",key="reg_pwd")

        if st.button("Register",key="reg_btn"):

            if name_reg and email_reg and pwd_reg:

                if save_user(name_reg,email_reg,pwd_reg):

                    # send welcome mail
                    send_registration_mail(email_reg,name_reg)

                    st.success("Registered Successfully ✅")
                    st.info("Check your email for confirmation")

                else:
                    st.error("User already exists")

            else:
                st.warning("Fill all fields")

# =====================================================
# MAIN APP AFTER LOGIN
# =====================================================
else:

    col1,col2=st.columns([6,1])

    with col1:
        st.success(f"Welcome, {st.session_state.user}")

    with col2:
        if st.button("Logout",key="logout_btn"):
            st.session_state.auth=False
            st.rerun()

    st.divider()

    import dashboard
    dashboard.main()



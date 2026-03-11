# =====================================================
# CRYPTO PORTFOLIO MANAGER - MAIN APP (FINAL CLEAN)
# =====================================================

import streamlit as st
import json
import os

# 👉 IMPORTANT (must be separate clean line)
from email_alert import send_registration_mail


# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Crypto Portfolio Manager",
    layout="wide"
)

# ---------------- USER DATABASE ----------------
USER_DB = "users.json"


# ---------------- LOAD USERS ----------------
def load_users():
    if not os.path.exists(USER_DB):
        return {}
    try:
        with open(USER_DB, "r") as f:
            return json.load(f)
    except:
        return {}


# ---------------- SAVE USER ----------------
def save_user(name, username, password):

    users = load_users()

    if username in users:
        return False

    users[username] = {
        "name": name,
        "password": password
    }

    with open(USER_DB, "w") as f:
        json.dump(users, f)

    # 👉 send email after registration
    send_registration_mail(username)

    return True


# ---------------- SESSION STATE ----------------
if "auth" not in st.session_state:
    st.session_state.auth = False

if "mode" not in st.session_state:
    st.session_state.mode = "login"


# =====================================================
# AUTH UI
# =====================================================
def auth_ui():

    st.title("🚀 Crypto Portfolio Manager")

    # ---------------- LOGIN ----------------
    if st.session_state.mode == "login":

        with st.form("login_form"):

            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            if st.form_submit_button("Login"):

                users = load_users()

                if username in users and users[username]["password"] == password:
                    st.session_state.auth = True
                    st.session_state.user = username
                    st.rerun()
                else:
                    st.error("Invalid username or password")

        if st.button("Create Account"):
            st.session_state.mode = "register"
            st.rerun()

    # ---------------- REGISTER ----------------
    else:

        with st.form("register_form"):

            name = st.text_input("Full Name")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            if st.form_submit_button("Register"):

                if name and username and password:

                    if save_user(name, username, password):
                        st.success("Registration successful!")
                        st.session_state.mode = "login"
                        st.rerun()
                    else:
                        st.error("Username already exists")

                else:
                    st.warning("Fill all fields")

        if st.button("Back to Login"):
            st.session_state.mode = "login"
            st.rerun()


# =====================================================
# MAIN FLOW
# =====================================================
if not st.session_state.auth:

    auth_ui()

else:

    st.write(f"👋 Welcome **{st.session_state.user}**")

    if st.button("Logout"):
        st.session_state.auth = False
        st.rerun()

    st.divider()

    # 👉 open dashboard
    import dashboard
    dashboard.main()

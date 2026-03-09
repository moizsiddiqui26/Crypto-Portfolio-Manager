# =====================================================
# CRYPTO PORTFOLIO MANAGER - FINAL APP
# =====================================================

import streamlit as st
import json
import os

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Crypto Portfolio Manager",layout="centered",initial_sidebar_state="collapsed")

# ---------------- USER DATABASE ----------------
USER_DB="users.json"

def load_users():
    if not os.path.exists(USER_DB):
        return {}
    try:
        with open(USER_DB,"r") as f:
            return json.load(f)
    except:
        return {}

def save_user(name,username,password):
    users=load_users()
    if username in users:
        return False
    users[username]={"name":name,"password":password}
    with open(USER_DB,"w") as f:
        json.dump(users,f)
    return True

# ---------------- SESSION STATE ----------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated=False
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode="login"
if "current_user" not in st.session_state:
    st.session_state.current_user=""

# ---------------- UI + COLOR SCHEME ----------------
st.markdown("""
<style>
header{visibility:hidden;}
[data-testid="stToolbar"]{display:none;}
[data-testid="stDecoration"]{display:none;}
[data-testid="stStatusWidget"]{display:none;}
footer{visibility:hidden;}
.block-container{padding-top:0rem!important;}

.stApp{background:linear-gradient(135deg,#0b0f1a,#111827,#1a1f2e);color:white;}

.app-title{text-align:center;font-size:38px;font-weight:800;background:linear-gradient(90deg,#a855f7,#22d3ee);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:25px;}

.auth-card{background:rgba(255,255,255,0.05);backdrop-filter:blur(14px);padding:40px;border-radius:20px;box-shadow:0 0 40px rgba(168,85,247,0.25);}

.auth-title{text-align:center;font-size:26px;font-weight:700;margin-bottom:20px;color:#e5e7eb;}

input{background:rgba(255,255,255,0.08)!important;border:1px solid rgba(255,255,255,0.15)!important;border-radius:10px!important;height:45px!important;color:white!important;}

div.stFormSubmitButton>button{background:linear-gradient(90deg,#a855f7,#22d3ee)!important;color:white!important;border:none!important;border-radius:10px!important;font-weight:bold!important;height:45px!important;transition:.3s ease;}
div.stFormSubmitButton>button:hover{box-shadow:0 0 20px rgba(168,85,247,.7);transform:scale(1.02);}

div.stButton>button{background:none!important;border:none!important;color:#22d3ee!important;text-decoration:underline!important;font-weight:bold!important;}

.welcome-text{font-size:22px;font-weight:600;color:#e5e7eb;}
</style>
""",unsafe_allow_html=True)

# ---------------- APP TITLE ----------------
st.markdown('<div class="app-title">🚀 Crypto Portfolio Manager</div>',unsafe_allow_html=True)

# ---------------- AUTH UI ----------------
def show_auth():
    col1,col2,col3=st.columns([1,2,1])
    with col2:
        st.markdown('<div class="auth-card">',unsafe_allow_html=True)

        if st.session_state.auth_mode=="login":
            st.markdown('<div class="auth-title">Portfolio Login</div>',unsafe_allow_html=True)

            with st.form("login_form"):
                username=st.text_input("Username",placeholder="Enter username")
                password=st.text_input("Password",type="password",placeholder="Enter password")

                if st.form_submit_button("Login"):
                    users=load_users()
                    if username in users and users[username]["password"]==password:
                        st.session_state.authenticated=True
                        st.session_state.current_user=users[username]["name"]
                        st.rerun()
                    else:
                        st.error("Invalid username or password")

            st.write("Don't have an account?")
            if st.button("Register"):
                st.session_state.auth_mode="register"
                st.rerun()

        else:
            st.markdown('<div class="auth-title">Create Portfolio Account</div>',unsafe_allow_html=True)

            with st.form("register_form"):
                name=st.text_input("Full Name",placeholder="Enter full name")
                username=st.text_input("Username",placeholder="Choose username")
                password=st.text_input("Password",type="password",placeholder="Create password")

                if st.form_submit_button("Register"):
                    if name and username and password:
                        if save_user(name,username,password):
                            st.session_state.auth_mode="login"
                            st.success("Registration successful")
                            st.rerun()
                        else:
                            st.error("Username already exists")
                    else:
                        st.warning("Please fill all fields")

            st.write("Already have an account?")
            if st.button("Login"):
                st.session_state.auth_mode="login"
                st.rerun()

        st.markdown('</div>',unsafe_allow_html=True)

# ---------------- LOGOUT ----------------
def logout():
    st.session_state.authenticated=False
    st.session_state.current_user=""
    st.session_state.auth_mode="login"
    st.rerun()

# ---------------- MAIN FLOW ----------------
if not st.session_state.authenticated:
    show_auth()
else:
    col1,col2=st.columns([5,1])
    with col1:
        st.markdown(f'<div class="welcome-text">👋 Welcome back, <b>{st.session_state.current_user}</b></div>',unsafe_allow_html=True)
    with col2:
        if st.button("Logout"):
            logout()
    st.divider()

    import dashboard
    dashboard.main()

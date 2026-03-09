# =====================================================
# CRYPTO PORTFOLIO MANAGER - PREMIUM UI APP
# =====================================================

import streamlit as st
import json
import os

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Crypto Portfolio Manager",layout="wide",initial_sidebar_state="expanded")

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

# ---------------- PREMIUM UI ----------------
st.markdown("""
<style>

/* BACKGROUND */
.stApp{background:linear-gradient(135deg,#0b0f1a,#0f172a,#020617);color:white}

/* SIDEBAR */
section[data-testid="stSidebar"]{
background:linear-gradient(180deg,#020617,#0f172a);
border-right:1px solid rgba(255,255,255,.05);
}

/* TITLE */
.app-title{
text-align:center;
font-size:42px;
font-weight:800;
background:linear-gradient(90deg,#a855f7,#22d3ee);
-webkit-background-clip:text;
-webkit-text-fill-color:transparent;
margin-top:10px;
}

/* CARD */
.auth-card{
background:rgba(255,255,255,.05);
backdrop-filter:blur(16px);
padding:40px;
border-radius:20px;
box-shadow:0 0 40px rgba(168,85,247,.2);
}

/* BUTTON */
div.stButton>button,div.stFormSubmitButton>button{
background:linear-gradient(90deg,#a855f7,#22d3ee)!important;
color:white!important;
border:none!important;
border-radius:10px!important;
font-weight:bold!important;
height:45px!important;
}

/* INPUT */
input{
background:rgba(255,255,255,.07)!important;
border-radius:10px!important;
color:white!important;
}

</style>
""",unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.markdown('<div class="app-title">🚀 Crypto Portfolio Manager</div>',unsafe_allow_html=True)

# ---------------- AUTH UI ----------------
def show_auth():
    col1,col2,col3=st.columns([1,2,1])
    with col2:
        st.markdown('<div class="auth-card">',unsafe_allow_html=True)

        if st.session_state.auth_mode=="login":
            st.subheader("Login")

            with st.form("login_form"):
                username=st.text_input("Username")
                password=st.text_input("Password",type="password")

                if st.form_submit_button("Login"):
                    users=load_users()
                    if username in users and users[username]["password"]==password:
                        st.session_state.authenticated=True
                        st.session_state.current_user=users[username]["name"]
                        st.rerun()
                    else:
                        st.error("Invalid credentials")

            if st.button("Create Account"):
                st.session_state.auth_mode="register"
                st.rerun()

        else:
            st.subheader("Create Account")

            with st.form("register_form"):
                name=st.text_input("Full Name")
                username=st.text_input("Username")
                password=st.text_input("Password",type="password")

                if st.form_submit_button("Register"):
                    if save_user(name,username,password):
                        st.success("Registered successfully")
                        st.session_state.auth_mode="login"
                        st.rerun()
                    else:
                        st.error("Username exists")

            if st.button("Back to Login"):
                st.session_state.auth_mode="login"
                st.rerun()

        st.markdown("</div>",unsafe_allow_html=True)

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
    col1,col2=st.columns([6,1])
    with col1:
        st.write(f"👋 Welcome back, **{st.session_state.current_user}**")
    with col2:
        if st.button("Logout"):
            logout()

    st.divider()

    import dashboard
    dashboard.main()

# =========================================================
# CRYPTO RISK ANALYZER - AUTH APP (FINAL VERSION)
# =========================================================
# Features:
# ✔ Modern UI
# ✔ Header removed
# ✔ Login/Register system (JSON storage)
# ✔ Session handling
# ✔ Logout button
# ✔ Clean structure with comments (presentation ready)
# =========================================================

# ---------------- IMPORTS ----------------
import streamlit as st
import json
import os


# ---------------- PAGE CONFIG ----------------
# Configure page layout and title
st.set_page_config(
    page_title="Crypto Portfolio Manager",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# ---------------- USER DATABASE (LOCAL STORAGE) ----------------
# JSON file to store user data
USER_DB = "users.json"


def load_users():
    """
    Load all users from JSON file.
    Returns dictionary of users.
    """
    if not os.path.exists(USER_DB):
        return {}

    try:
        with open(USER_DB, "r") as f:
            return json.load(f)
    except:
        return {}


def save_user(name, username, password):
    """
    Save a new user if username not already exists.
    """
    users = load_users()

    if username in users:
        return False

    users[username] = {
        "name": name,
        "password": password
    }

    with open(USER_DB, "w") as f:
        json.dump(users, f)

    return True


# ---------------- SESSION STATE ----------------
# Maintain login state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

if "current_user" not in st.session_state:
    st.session_state.current_user = ""


# ---------------- CUSTOM UI (HEADER REMOVED + MODERN STYLE) ----------------
st.markdown("""
<style>

/* -------- REMOVE STREAMLIT HEADER -------- */
header {visibility: hidden;}
[data-testid="stToolbar"] {display: none;}
[data-testid="stDecoration"] {display: none;}
[data-testid="stStatusWidget"] {display: none;}
footer {visibility: hidden;}

.block-container {
    padding-top: 0rem !important;
}

/* -------- BACKGROUND -------- */
.stApp {
    background: linear-gradient(135deg,#0d1b2a,#1b263b,#415a77);
}

/* -------- CENTER CARD -------- */
.auth-card {
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(12px);
    padding: 40px;
    border-radius: 18px;
    box-shadow: 0px 10px 30px rgba(0,0,0,0.35);
}

/* -------- TITLE -------- */
.auth-title {
    color: #4cc9f0;
    text-align: center;
    font-size: 32px;
    font-weight: 800;
    margin-bottom: 25px;
}

/* -------- INPUT -------- */
input {
    border-radius: 10px !important;
    height: 45px !important;
}

/* -------- BUTTON -------- */
div.stFormSubmitButton > button {
    background: linear-gradient(90deg,#4cc9f0,#4895ef) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: bold !important;
    height: 45px !important;
}

/* -------- LINK BUTTON -------- */
div.stButton > button {
    background: none !important;
    border: none !important;
    color: #4cc9f0 !important;
    text-decoration: underline !important;
    font-weight: bold !important;
}

</style>
""", unsafe_allow_html=True)


# ---------------- AUTH UI FUNCTION ----------------
def show_auth():
    """
    Display Login / Register UI
    """

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)

        # ---------------- LOGIN PAGE ----------------
        if st.session_state.auth_mode == "login":

            st.markdown('<div class="auth-title">Sign In</div>', unsafe_allow_html=True)

            with st.form("login_form"):

                username = st.text_input("Username", placeholder="Enter username")
                password = st.text_input("Password", type="password", placeholder="Enter password")

                if st.form_submit_button("Login"):

                    users = load_users()

                    if username in users and users[username]["password"] == password:
                        st.session_state.authenticated = True
                        st.session_state.current_user = users[username]["name"]
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")

            st.write("Don't have an account?")
            if st.button("Register"):
                st.session_state.auth_mode = "register"
                st.rerun()

        # ---------------- REGISTER PAGE ----------------
        else:

            st.markdown('<div class="auth-title">Register</div>', unsafe_allow_html=True)

            with st.form("register_form"):

                name = st.text_input("Full Name", placeholder="Enter full name")
                username = st.text_input("Username", placeholder="Choose username")
                password = st.text_input("Password", type="password", placeholder="Create password")

                if st.form_submit_button("Register"):

                    if name and username and password:

                        if save_user(name, username, password):
                            st.success("Registration successful!")
                            st.session_state.auth_mode = "login"
                            st.rerun()
                        else:
                            st.error("Username already exists")

                    else:
                        st.warning("Please fill all fields")

            st.write("Already have an account?")
            if st.button("Login"):
                st.session_state.auth_mode = "login"
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)


# ---------------- LOGOUT FUNCTION ----------------
def logout():
    """Clear session and logout user"""
    st.session_state.authenticated = False
    st.session_state.current_user = ""
    st.session_state.auth_mode = "login"
    st.rerun()


# ---------------- MAIN FLOW ----------------
if not st.session_state.authenticated:

    # Show login/register UI
    show_auth()

else:

    # Top welcome + logout row
    col1, col2 = st.columns([5, 1])

    with col1:
        st.markdown(f"### 👋 Welcome, **{st.session_state.current_user}**")

    with col2:
        if st.button("Logout"):
            logout()

    st.divider()

    # Open dashboard module after login
    import dashboard
    dashboard.main()

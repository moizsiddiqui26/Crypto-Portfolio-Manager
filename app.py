# ---------------- IMPORTS ----------------
# Streamlit for UI, json for local storage, os for file handling
import streamlit as st
import json
import os


# ---------------- PAGE CONFIGURATION ----------------
# Sets page title, layout and removes sidebar initially
st.set_page_config(
    page_title="Crypto Risk Analyzer",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# ---------------- USER DATABASE (Local JSON Storage) ----------------
# File where user data will be stored
USER_DB = "users.json"


# Function: Load users from JSON file
def load_users():
    """Load user data from JSON file."""
    if not os.path.exists(USER_DB):
        return {}
    try:
        with open(USER_DB, "r") as f:
            return json.load(f)
    except:
        return {}


# Function: Save new user to JSON file
def save_user(name, username, password):
    """Save a new user if username not already taken."""
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


# ---------------- SESSION STATE SETUP ----------------
# Maintains login session
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"


# ---------------- CUSTOM UI STYLING ----------------
st.markdown("""
<style>

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

/* -------- INPUT FIELDS -------- */
input {
    border-radius: 10px !important;
    height: 45px !important;
}

/* -------- BUTTON STYLE -------- */
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
    """Displays Login/Register UI"""

    # Create centered layout
    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)

        # ---------------- LOGIN PAGE ----------------
        if st.session_state.auth_mode == "login":

            st.markdown('<div class="auth-title">Sign In</div>', unsafe_allow_html=True)

            # Login form
            with st.form("login_form"):

                username = st.text_input("Username", placeholder="Enter username")
                password = st.text_input("Password", type="password", placeholder="Enter password")

                # Login button
                if st.form_submit_button("Login"):

                    users = load_users()

                    if username in users and users[username]["password"] == password:
                        st.session_state.authenticated = True
                        st.session_state.current_user = users[username]["name"]
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")

            # Toggle to register page
            st.write("Don't have an account?")
            if st.button("Register"):
                st.session_state.auth_mode = "register"
                st.rerun()

        # ---------------- REGISTER PAGE ----------------
        else:

            st.markdown('<div class="auth-title">Register</div>', unsafe_allow_html=True)

            # Register form
            with st.form("register_form"):

                name = st.text_input("Full Name", placeholder="Enter full name")
                username = st.text_input("Username", placeholder="Choose username")
                password = st.text_input("Password", type="password", placeholder="Create password")

                # Register button
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

            # Toggle to login page
            st.write("Already have an account?")
            if st.button("Login"):
                st.session_state.auth_mode = "login"
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)


# ---------------- MAIN APP FLOW ----------------
if not st.session_state.authenticated:

    # Show authentication screen first
    show_auth()

else:
    # If logged in → open dashboard module
    import dashboard
    dashboard.main()

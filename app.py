import streamlit as st
import json,os

st.set_page_config(page_title="Crypto Portfolio Manager",layout="wide")

USER_DB="users.json"

def load_users():
    if not os.path.exists(USER_DB):
        return {}
    with open(USER_DB,"r") as f:
        return json.load(f)

def save_user(name,u,p):
    users=load_users()
    if u in users: return False
    users[u]={"name":name,"password":p}
    with open(USER_DB,"w") as f: json.dump(users,f)
    return True

if "auth" not in st.session_state: st.session_state.auth=False
if "mode" not in st.session_state: st.session_state.mode="login"

def login_ui():
    st.title("🚀 Crypto Portfolio Manager")

    if st.session_state.mode=="login":
        with st.form("login"):
            u=st.text_input("Username")
            p=st.text_input("Password",type="password")
            if st.form_submit_button("Login"):
                users=load_users()
                if u in users and users[u]["password"]==p:
                    st.session_state.auth=True
                    st.session_state.user=users[u]["name"]
                    st.rerun()
                else: st.error("Invalid login")

        if st.button("Register"): st.session_state.mode="register";st.rerun()

    else:
        with st.form("reg"):
            n=st.text_input("Name")
            u=st.text_input("Username")
            p=st.text_input("Password",type="password")
            if st.form_submit_button("Register"):
                if save_user(n,u,p): st.success("Registered");st.session_state.mode="login";st.rerun()
                else: st.error("User exists")

        if st.button("Back"): st.session_state.mode="login";st.rerun()

if not st.session_state.auth:
    login_ui()
else:
    st.write(f"Welcome {st.session_state.user}")
    if st.button("Logout"): st.session_state.auth=False;st.rerun()

    import dashboard
    dashboard.main()

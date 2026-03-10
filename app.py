import streamlit as st, json, os
from email_alert import send_registration_mail

st.set_page_config(page_title="Crypto Investment Manager",layout="wide")

USER_DB="users.json"

def load_users():
    if not os.path.exists(USER_DB): return {}
    with open(USER_DB) as f: return json.load(f)

def save_user(name,email,password):
    users=load_users()
    if email in users: return False
    users[email]={"name":name,"password":password}
    with open(USER_DB,"w") as f: json.dump(users,f)
    return True

if "auth" not in st.session_state: st.session_state.auth=False

# ---------------- LOGIN ----------------
if not st.session_state.auth:

    st.title("🚀 Crypto Investment Manager")

    tab1,tab2=st.tabs(["Login","Register"])

    with tab1:
        email=st.text_input("Email")
        pwd=st.text_input("Password",type="password")

        if st.button("Login"):
            users=load_users()
            if email in users and users[email]["password"]==pwd:
                st.session_state.auth=True
                st.session_state.user=email
                st.rerun()
            else: st.error("Invalid credentials")

    with tab2:
        name=st.text_input("Name")
        email=st.text_input("Register Email")
        pwd=st.text_input("Password",type="password")

        if st.button("Register"):
            if save_user(name,email,pwd):
                send_registration_mail(email,name)
                st.success("Registered + Email Sent")
            else: st.error("User exists")

else:
    st.success(f"Welcome {st.session_state.user}")
    if st.button("Logout"):
        st.session_state.auth=False
        st.rerun()

    import dashboard
    dashboard.main()

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
tab1,tab2=st.tabs(["Login","Register"])

# ---------------- LOGIN ----------------
with tab1:
    email_login=st.text_input("Email",key="login_email")
    pwd_login=st.text_input("Password",type="password",key="login_pwd")

    if st.button("Login",key="login_btn"):
        users=load_users()
        if email_login in users and users[email_login]["password"]==pwd_login:
            st.session_state.auth=True
            st.session_state.user=email_login
            st.rerun()
        else:
            st.error("Invalid credentials")

# ---------------- REGISTER ----------------
with tab2:
    name_reg=st.text_input("Name",key="reg_name")
    email_reg=st.text_input("Register Email",key="reg_email")
    pwd_reg=st.text_input("Password",type="password",key="reg_pwd")

    if st.button("Register",key="reg_btn"):
        if save_user(name_reg,email_reg,pwd_reg):
            send_registration_mail(email_reg,name_reg)
            st.success("Registered + Email Sent")
        else:
            st.error("User exists")
else:
    st.success(f"Welcome {st.session_state.user}")
    if st.button("Logout"):
        st.session_state.auth=False
        st.rerun()

    import dashboard
    dashboard.main()


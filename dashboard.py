import streamlit as st
import pandas as pd
import plotly.express as px
from risk_predictor import run_risk_checks
from email_alert import send_alert

@st.cache_data
def load_data():
    df=pd.read_csv("preprocessed_data.csv")
    df["Date"]=pd.to_datetime(df["Date"])
    return df

def main():

    df=load_data()

    page=st.sidebar.radio("Navigation",[
    "User Profile","Investment Mix Calculator","Risk Checker"])

    # =================================================
# USER PROFILE PAGE
# =================================================
if page=="👤 User Profile":

    import json,os

    st.header("👤 User Profile")

    user=st.session_state.get("user","Guest")

    st.subheader(f"Welcome, {user}")

    HOLDINGS_FILE="holdings.json"

    # ---------- LOAD HOLDINGS ----------
    if os.path.exists(HOLDINGS_FILE):
        with open(HOLDINGS_FILE,"r") as f:
            all_holdings=json.load(f)
    else:
        all_holdings={}

    if user not in all_holdings:
        all_holdings[user]={}

    holdings=all_holdings[user]

    # ---------- ADD HOLDINGS ----------
    st.subheader("➕ Add Holdings")

    cryptos=sorted(df["Crypto"].unique())

    col1,col2=st.columns(2)

    with col1:
        coin=st.selectbox("Crypto",cryptos)

    with col2:
        amount=st.number_input("Amount Held",min_value=0.0,value=0.0)

    if st.button("Add / Update Holding"):

        holdings[coin]=amount
        all_holdings[user]=holdings

        with open(HOLDINGS_FILE,"w") as f:
            json.dump(all_holdings,f)

        st.success("Holding Updated")

    st.divider()

    # ---------- SHOW HOLDINGS ----------
    st.subheader("📊 Your Portfolio")

    if holdings:

        latest=df.sort_values("Date").groupby("Crypto").tail(1)

        rows=[]
        total_value=0

        for coin,amt in holdings.items():

            price=float(latest[latest["Crypto"]==coin]["Close"])

            value=amt*price
            total_value+=value

            rows.append([coin,amt,price,value])

        table=pd.DataFrame(rows,columns=["Crypto","Amount","Price","Value ($)"])

        st.metric("💰 Total Portfolio Value",f"${total_value:,.2f}")

        st.dataframe(table,use_container_width=True)

        # ---------- PIE CHART ----------
        fig=px.pie(table,names="Crypto",values="Value ($)",hole=0.4,
                   title="Portfolio Allocation")

        st.plotly_chart(fig,use_container_width=True)

    else:
        st.info("No holdings added yet")
    # ---------------- MIX CALCULATOR ----------------
    if page=="Investment Mix Calculator":

        st.header("⚙ Investment Mix Calculator")

        amount=st.number_input("Amount",value=1000.0)
        risk=st.selectbox("Risk Level",["Low","Medium","High"])

        returns=df.groupby("Crypto").apply(lambda x:(x.Close.iloc[-1]-x.Close.iloc[0])/x.Close.iloc[0]).reset_index(name="Return")
        vol=df.groupby("Crypto")["Close"].std().reset_index(name="Vol")

        m=returns.merge(vol,on="Crypto")
        m["Return_n"]=m.Return/m.Return.max()
        m["Vol_n"]=m.Vol/m.Vol.max()

        if risk=="Low": m["Score"]=.7*(1-m.Vol_n)+.3*m.Return_n
        elif risk=="Medium": m["Score"]=.5*(1-m.Vol_n)+.5*m.Return_n
        else: m["Score"]=.3*(1-m.Vol_n)+.7*m.Return_n

        m["Allocation %"]=m.Score/m.Score.sum()*100
        m["Investment"]=m["Allocation %"]/100*amount

        st.dataframe(m[["Crypto","Allocation %","Investment"]])

        st.plotly_chart(px.pie(m,names="Crypto",values="Investment"),use_container_width=True)

        csv=m.to_csv(index=False)
        st.download_button("Download CSV",csv,"investment.csv")

    # ---------------- RISK CHECKER ----------------
    if page=="Risk Checker":

        st.header("⚠ Risk Checker + Predictor")

        if st.button("Run Risk Check"):
            result=run_risk_checks(df)

            st.dataframe(result)

            if (result["Risk"]=="High").any():
                send_alert(result)
                st.warning("Alert sent!")

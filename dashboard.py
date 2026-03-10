import streamlit as st
import pandas as pd
import plotly.express as px
from crypto_api import fetch_crypto_prices
from risk_predictor import run_risk_checks
from email_alert import send_alert

def main():

    df=fetch_crypto_prices()

    page=st.sidebar.radio("Navigation",[
    "Dashboard","Investment Mix Calculator","Risk Checker"
    ])

# ---------------- DASHBOARD ----------------
    if page=="Dashboard":

        st.header("📊 Live Crypto Dashboard")

        st.dataframe(df,use_container_width=True)

        fig=px.bar(df,x="Crypto",y="Price",color="Crypto")
        st.plotly_chart(fig,use_container_width=True)

# ---------------- MIX CALCULATOR ----------------
    if page=="Investment Mix Calculator":

        st.header("⚙ Investment Mix Calculator")

        amount=st.number_input("Amount",value=1000.0)
        risk=st.selectbox("Risk Level",["Low","Medium","High"])

        # fake volatility + return for demo
        df["Return"]=df["Price"]/df["Price"].max()
        df["Vol"]=df["Price"]/df["Price"].mean()

        df["Return_n"]=df["Return"]/df["Return"].max()
        df["Vol_n"]=df["Vol"]/df["Vol"].max()

        if risk=="Low": df["Score"]=.7*(1-df.Vol_n)+.3*df.Return_n
        elif risk=="Medium": df["Score"]=.5*(1-df.Vol_n)+.5*df.Return_n
        else: df["Score"]=.3*(1-df.Vol_n)+.7*df.Return_n

        df["Allocation %"]=df.Score/df.Score.sum()*100
        df["Investment"]=df["Allocation %"]/100*amount

        st.dataframe(df[["Crypto","Allocation %","Investment"]])

        fig2=px.pie(df,names="Crypto",values="Investment")
        st.plotly_chart(fig2,use_container_width=True)

        csv=df.to_csv(index=False)
        st.download_button("Download CSV",csv,"investment.csv")

# ---------------- RISK CHECKER ----------------
    if page=="Risk Checker":

        st.header("⚠ Risk Checker")

        if st.button("Run Risk Check"):

            result=run_risk_checks(df)

            st.dataframe(result)

            if (result["Risk"]=="High").any():
                send_alert(result)
                st.warning("Email Alert Sent!")

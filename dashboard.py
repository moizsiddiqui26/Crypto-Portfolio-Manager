import streamlit as st
import plotly.express as px
from crypto_api import fetch_data
from mix_calculator import calculate_mix
from risk_predictor import run_risk
from report_saver import save_csv
from email_alert import send_alert

def main():

    df=fetch_data()

    page=st.sidebar.radio("Navigation",
    ["Dashboard","Investment Mix","Risk Checker"])

# DASHBOARD
    if page=="Dashboard":
        st.header("Live Crypto Dashboard")
        st.dataframe(df)
        st.plotly_chart(px.bar(df,x="Crypto",y="Price"))

# MIX
    if page=="Investment Mix":
        amt=st.number_input("Amount",1000.0)
        risk=st.selectbox("Risk",["Low","Medium","High"])

        result=calculate_mix(df,amt,risk)

        st.dataframe(result[["Crypto","Allocation %","Investment"]])
        st.plotly_chart(px.pie(result,names="Crypto",values="Investment"))

        st.download_button("Download CSV",save_csv(result),"mix.csv")

# RISK
    if page=="Risk Checker":
        if st.button("Run"):
            r=run_risk(df)
            st.dataframe(r)
            if (r.Risk=="High").any():
                send_alert(r)
                st.warning("Alert Sent")

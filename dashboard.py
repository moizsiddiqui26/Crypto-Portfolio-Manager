# =====================================================
# CRYPTO INVESTMENT MANAGER - PRO DASHBOARD
# =====================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import os
from crypto_api import fetch_data
from risk_predictor import run_risk
from email_alert import send_alert

HISTORY_FILE="investment_history.csv"

# =====================================================
# SAVE USER INVESTMENT HISTORY
# =====================================================
def save_history(user,df):
    df["User"]=user
    if os.path.exists(HISTORY_FILE):
        old=pd.read_csv(HISTORY_FILE)
        df=pd.concat([old,df])
    df.to_csv(HISTORY_FILE,index=False)

def load_history(user):
    if not os.path.exists(HISTORY_FILE):
        return pd.DataFrame()
    df=pd.read_csv(HISTORY_FILE)
    return df[df["User"]==user]


# =====================================================
# MAIN
# =====================================================
def main():

    df=fetch_data()

    page=st.sidebar.radio("📂 Navigation",
    ["📊 Dashboard (EDA)","💼 Smart Investment Mix","⚠ Risk Checker"])

# =====================================================
# 1️⃣ DASHBOARD + EDA
# =====================================================
    if page=="📊 Dashboard (EDA)":

        st.markdown("## 📊 Crypto Market Analysis")

        st.dataframe(df,use_container_width=True)

        col1,col2=st.columns(2)

        with col1:
            fig=px.bar(df,x="Crypto",y="Price",
                       title="Live Price Comparison")
            st.plotly_chart(fig,use_container_width=True)

        with col2:
            fig2=px.pie(df,names="Crypto",values="Price",
                        title="Market Distribution")
            st.plotly_chart(fig2,use_container_width=True)

        # ---------- EXTRA EDA ----------
        st.markdown("### 📈 Price Distribution")
        fig3=px.box(df,y="Price",points="all")
        st.plotly_chart(fig3,use_container_width=True)

        st.markdown("### 🔎 Statistical Summary")
        st.write(df.describe())

# =====================================================
# 2️⃣ SMART MIX CALCULATOR
# =====================================================
    if page=="💼 Smart Investment Mix":

        st.markdown("## 💼 Smart Investment Strategy Builder")

        st.info("Uses past crypto price behavior to determine best strategy.")

        col1,col2=st.columns(2)

        with col1:
            amount=st.number_input("💰 Enter Amount",
                                   min_value=100.0,value=1000.0,
                                   step=100.0,key="smart_amt")

        with col2:
            risk=st.selectbox("📊 Investment Level",
                              ["Low","Medium","High"],
                              key="smart_lvl")

        # ---------------- CALCULATE ----------------
        if st.button("🚀 Calculate Strategy",use_container_width=True):

            # --- risk score using past price spread ---
            df["Return"]=df.Price/df.Price.max()
            df["Volatility"]=df.Price/df.Price.mean()

            if risk=="Low":
                df["Score"]=0.7*(1-df.Volatility)+0.3*df.Return
                strategy="Focus on stable coins with consistent returns."

            elif risk=="Medium":
                df["Score"]=0.5*(1-df.Volatility)+0.5*df.Return
                strategy="Balanced portfolio across major cryptos."

            else:
                df["Score"]=0.3*(1-df.Volatility)+0.7*df.Return
                strategy="Aggressive strategy targeting growth coins."

            df["Allocation %"]=df.Score/df.Score.sum()*100
            df["Investment"]=df["Allocation %"]/100*amount

            st.divider()

            # ---------- TABLE ----------
            st.subheader("📋 Investment Strategy Table")
            show=df[["Crypto","Allocation %","Investment"]]
            st.dataframe(show,use_container_width=True)

            # ---------- CHART ----------
            st.subheader("📊 Strategy Visualization")
            fig=px.pie(show,names="Crypto",values="Investment",hole=0.4)
            st.plotly_chart(fig,use_container_width=True)

            # ---------- SAVE HISTORY ----------
            save_history(st.session_state.user,show)

            # ---------- STRATEGY TEXT ----------
            st.success(f"📌 Recommended Strategy: {strategy}")

            # ---------- CSV ----------
            st.download_button("⬇ Download Strategy CSV",
                               show.to_csv(index=False),
                               "strategy.csv",
                               use_container_width=True)

        # ---------- USER HISTORY ----------
        st.divider()
        st.markdown("## 📈 Your Past Investments")

        hist=load_history(st.session_state.user)

        if not hist.empty:

            st.dataframe(hist,use_container_width=True)

            st.markdown("### 📊 Investment Growth Trend")

            fig_hist=px.line(hist,x=hist.index,y="Investment",
                             color="Crypto",
                             title="Past Investment Growth")

            st.plotly_chart(fig_hist,use_container_width=True)

        else:
            st.info("No past investments yet.")

# =====================================================
# 3️⃣ RISK CHECKER (UPGRADED UI)
# =====================================================
    if page=="⚠ Risk Checker":

        st.markdown("## ⚠ Parallel Risk Checker")

        st.write("Analyzes crypto volatility using parallel processing.")

        if st.button("🔍 Run Risk Analysis",use_container_width=True):

            result=run_risk(df)

            st.subheader("📋 Risk Table")
            st.dataframe(result,use_container_width=True)

            st.subheader("📊 Risk Visualization")

            fig=px.bar(result,x="Crypto",y="Price",
                       color="Risk",title="Risk Comparison")

            st.plotly_chart(fig,use_container_width=True)

            if (result["Risk"]=="High").any():
                send_alert(result)
                st.warning("🚨 High Risk Alert Sent!")

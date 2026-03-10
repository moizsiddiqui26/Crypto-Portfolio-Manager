# =====================================================
# CRYPTO INVESTMENT MANAGER - PREMIUM DASHBOARD
# =====================================================

import streamlit as st
import plotly.express as px
from crypto_api import fetch_data
from mix_calculator import calculate_mix
from risk_predictor import run_risk
from report_saver import save_csv
from email_alert import send_alert


# =====================================================
# MAIN FUNCTION
# =====================================================
def main():

    df=fetch_data()

    page=st.sidebar.radio("📂 Navigation",
    ["📊 Dashboard","💼 Investment Mix","⚠ Risk Checker"])


# =====================================================
# DASHBOARD PAGE
# =====================================================
    if page=="📊 Dashboard":

        st.markdown("## 📊 Live Crypto Dashboard")

        st.dataframe(df,use_container_width=True)

        fig=px.bar(df,x="Crypto",y="Price",color="Crypto",
                   title="Live Crypto Prices")

        st.plotly_chart(fig,use_container_width=True)


# =====================================================
# UPGRADED INVESTMENT MIX
# =====================================================
    if page=="💼 Investment Mix":

        st.markdown("## 💼 Smart Investment Mix Calculator")

        st.write("""
Plan your crypto investment using a rule-based strategy.
Enter amount + choose risk level → get optimized allocation.
""")

        col1,col2=st.columns(2)

        with col1:
            amount=st.number_input("💰 Enter Amount ($)",
                                   min_value=100.0,value=1000.0,
                                   step=100.0,key="mix_amt")

        with col2:
            risk=st.selectbox("📊 Investment Level",
                              ["Low","Medium","High"],
                              key="mix_lvl")

        if st.button("🚀 Calculate Mix",use_container_width=True):

            result=calculate_mix(df.copy(),amount,risk)

            st.divider()

            st.subheader("📋 Investment Breakdown")

            show_df=result[["Crypto","Allocation %","Investment"]]
            st.dataframe(show_df,use_container_width=True)

            st.subheader("📊 Distribution Chart")

            fig=px.pie(result,names="Crypto",values="Investment",
                       hole=0.4,title="Portfolio Allocation")

            st.plotly_chart(fig,use_container_width=True)

            csv=save_csv(result)

            st.download_button("⬇ Download CSV",csv,
                               "investment_mix_report.csv",
                               use_container_width=True)

        # ---------- LEVEL DESCRIPTION ----------
        st.divider()
        st.markdown("## 📘 Investment Level Guide")

        c1,c2,c3=st.columns(3)

        c1.markdown("""### 🟢 Low Risk
• Stable coins focus  
• Less volatility  
• Safer growth  
""")

        c2.markdown("""### 🟡 Medium Risk
• Balanced strategy  
• Moderate returns  
• Medium volatility  
""")

        c3.markdown("""### 🔴 High Risk
• Growth-focused  
• High volatility  
• Higher returns  
""")


# =====================================================
# UPGRADED RISK CHECKER
# =====================================================
    if page=="⚠ Risk Checker":

        st.markdown("## ⚠ Smart Risk Checker & Predictor")

        st.write("""
Analyze crypto risk using parallel processing.  
Click below to detect risky assets instantly.
""")

        if st.button("🔍 Run Risk Analysis",use_container_width=True):

            result=run_risk(df)

            st.divider()

            # ---------- RESULT TABLE ----------
            st.subheader("📋 Risk Report")
            st.dataframe(result,use_container_width=True)

            # ---------- CHART ----------
            st.subheader("📊 Risk Distribution")

            fig=px.bar(result,x="Crypto",y="Price",
                       color="Risk",
                       title="Crypto Risk Levels")

            st.plotly_chart(fig,use_container_width=True)

            # ---------- CSV ----------
            csv=save_csv(result)

            st.download_button("⬇ Download Risk Report",
                               csv,
                               "risk_report.csv",
                               use_container_width=True)

            # ---------- ALERT ----------
            if (result["Risk"]=="High").any():
                send_alert(result)
                st.warning("🚨 High Risk Detected — Email Alert Sent!")

        # ---------- RISK LEVEL GUIDE ----------
        st.divider()

        st.markdown("## 📘 Risk Level Guide")

        r1,r2,r3=st.columns(3)

        r1.markdown("""### 🟢 Low Risk
• Stable movement  
• Lower volatility  
• Safer investments  
""")

        r2.markdown("""### 🟡 Medium Risk
• Moderate movement  
• Balanced volatility  
• Normal trading risk  
""")

        r3.markdown("""### 🔴 High Risk
• Highly volatile  
• Big price swings  
• Requires caution  
""")

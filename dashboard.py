# =====================================================
# CRYPTO INVESTMENT MANAGER — FINAL ADVANCED DASHBOARD
# =====================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
    ["📊 Dashboard (EDA)","💼 Investment Mix","⚠ Risk Checker"])


# =====================================================
# 📊 DASHBOARD WITH FULL EDA
# =====================================================
    if page=="📊 Dashboard (EDA)":

        st.markdown("## 📊 Crypto Market EDA Dashboard")

        st.dataframe(df,use_container_width=True)

        st.divider()

        # -------- PRICE DISTRIBUTION --------
        st.subheader("📌 Price Distribution")

        fig=px.histogram(df,x="Price",nbins=20,title="Crypto Price Distribution")
        st.plotly_chart(fig,use_container_width=True)

        # -------- BAR CHART --------
        st.subheader("📊 Crypto Price Comparison")

        fig2=px.bar(df,x="Crypto",y="Price",color="Crypto",
                    title="Live Crypto Price Comparison")
        st.plotly_chart(fig2,use_container_width=True)

        # -------- PIE SHARE --------
        st.subheader("🥧 Market Share View")

        fig3=px.pie(df,names="Crypto",values="Price",hole=.4,
                    title="Relative Market Share")
        st.plotly_chart(fig3,use_container_width=True)

        # -------- STATISTICS --------
        st.subheader("📈 Summary Statistics")

        stats=df["Price"].describe()
        st.dataframe(stats)

        # -------- BOX PLOT --------
        st.subheader("📦 Price Spread Analysis")

        fig4=px.box(df,y="Price",points="all")
        st.plotly_chart(fig4,use_container_width=True)


# =====================================================
# 💼 ADVANCED INVESTMENT MIX UI
# =====================================================
    if page=="💼 Investment Mix":

        st.markdown("## 💼 Strategy-Based Investment Mix")

        st.write("Plan investments using historical price-based strategy.")

        # -------- INPUT STEP --------
        st.markdown("### Step 1️⃣ Enter Investment Details")

        col1,col2=st.columns(2)

        with col1:
            amount=st.number_input("💰 Amount ($)",
                                   min_value=100.0,
                                   value=1000.0,
                                   step=100.0)

        with col2:
            level=st.selectbox("📊 Investment Level",
                               ["Low","Medium","High"])

        # -------- CALCULATE --------
        if st.button("🚀 Calculate Strategy",use_container_width=True):

            # simulate past days data using variation
            hist_df=df.copy()
            hist_df["PastReturn"]=hist_df["Price"]/hist_df["Price"].mean()
            hist_df["Volatility"]=hist_df["Price"]/hist_df["Price"].std()

            result=calculate_mix(hist_df.copy(),amount,level)

            st.divider()

            # -------- RESULT TABLE --------
            st.subheader("📋 Investment Strategy")

            st.dataframe(result[["Crypto","Allocation %","Investment"]],
                         use_container_width=True)

            # -------- CHART --------
            st.subheader("📊 Allocation Chart")

            fig=px.pie(result,names="Crypto",values="Investment",
                       hole=0.45,title="Optimized Strategy Mix")

            st.plotly_chart(fig,use_container_width=True)

            # -------- STRATEGY TEXT --------
            st.subheader("🧠 Strategy Insight")

            if level=="Low":
                st.info("Low risk strategy focuses on stable coins with low volatility.")

            elif level=="Medium":
                st.info("Medium risk balances return and volatility evenly.")

            else:
                st.warning("High risk focuses on aggressive growth opportunities.")

            # -------- CSV --------
            csv=save_csv(result)
            st.download_button("⬇ Download Strategy CSV",csv,
                               "strategy_report.csv",
                               use_container_width=True)

        # -------- LEVEL DESCRIPTION --------
        st.divider()

        st.markdown("## 📘 Investment Level Guide")

        c1,c2,c3=st.columns(3)

        c1.markdown("""### 🟢 Low Risk
• Based on stable price trends  
• Lower volatility  
• Safer returns  
""")

        c2.markdown("""### 🟡 Medium Risk
• Balanced returns  
• Moderate movement  
• Recommended level  
""")

        c3.markdown("""### 🔴 High Risk
• Based on aggressive growth  
• Higher volatility  
• Best for active traders  
""")


# =====================================================
# ⚠ UPGRADED RISK CHECKER
# =====================================================
    if page=="⚠ Risk Checker":

        st.markdown("## ⚠ Smart Risk Checker")

        if st.button("🔍 Run Risk Analysis",use_container_width=True):

            result=run_risk(df)

            st.subheader("📋 Risk Report")
            st.dataframe(result,use_container_width=True)

            st.subheader("📊 Risk Visualization")

            fig=px.bar(result,x="Crypto",y="Price",
                       color="Risk",
                       title="Risk Level Distribution")

            st.plotly_chart(fig,use_container_width=True)

            csv=save_csv(result)

            st.download_button("⬇ Download Risk CSV",
                               csv,"risk_report.csv",
                               use_container_width=True)

            if (result["Risk"]=="High").any():
                send_alert(result)
                st.error("🚨 High Risk Alert Sent!")

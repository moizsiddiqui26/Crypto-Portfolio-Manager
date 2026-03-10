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


# UPGRADED INVESTMENT MIX UI
# =================================================
if page=="Investment Mix":

    st.markdown("## 💼 Smart Investment Mix Calculator")

    st.write("""
Plan your crypto investment using a rule-based strategy.
Enter amount + choose risk level → get optimized allocation.
""")

    # ---------------- INPUT CARD ----------------
    with st.container():

        col1,col2=st.columns(2)

        with col1:
            amount=st.number_input(
                "💰 Enter Amount to Invest ($)",
                min_value=100.0,
                value=1000.0,
                step=100.0,
                key="mix_amount"
            )

        with col2:
            risk=st.selectbox(
                "📊 Select Investment Level",
                ["Low","Medium","High"],
                key="mix_level"
            )

    # ---------------- SUBMIT BUTTON ----------------
    if st.button("🚀 Calculate Investment Mix",use_container_width=True):

        from mix_calculator import calculate_mix

        result=calculate_mix(df.copy(),amount,risk)

        st.divider()

        # ---------------- RESULT TABLE ----------------
        st.subheader("📋 Investment Breakdown")

        show_df=result[["Crypto","Allocation %","Investment"]]

        st.dataframe(show_df,use_container_width=True)

        # ---------------- CHART ----------------
        import plotly.express as px

        st.subheader("📊 Investment Distribution")

        fig=px.pie(
            result,
            names="Crypto",
            values="Investment",
            hole=0.4,
            title="Optimized Portfolio Allocation"
        )

        st.plotly_chart(fig,use_container_width=True)

        # ---------------- CSV DOWNLOAD ----------------
        csv=result.to_csv(index=False)

        st.download_button(
            "⬇ Download Report (CSV)",
            csv,
            "investment_mix_report.csv",
            use_container_width=True
        )

    # =================================================
    # LEVEL DESCRIPTION (BOTTOM SECTION)
    # =================================================
    st.divider()

    st.markdown("## 📘 Investment Level Guide")

    col1,col2,col3=st.columns(3)

    with col1:
        st.markdown("""
### 🟢 Low Risk
• Focus on stable coins  
• Less volatility  
• Slow but safer growth  
• Best for beginners
""")

    with col2:
        st.markdown("""
### 🟡 Medium Risk
• Balanced strategy  
• Moderate returns  
• Moderate volatility  
• Good for regular investors
""")

    with col3:
        st.markdown("""
### 🔴 High Risk
• Focus on high-growth coins  
• High volatility  
• Higher return potential  
• Best for experienced traders
""")
# RISK
    if page=="Risk Checker":
        if st.button("Run"):
            r=run_risk(df)
            st.dataframe(r)
            if (r.Risk=="High").any():
                send_alert(r)
                st.warning("Alert Sent")

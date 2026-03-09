import streamlit as st
import pandas as pd
import plotly.express as px 
@st.cache_data
def load_data():
    return pd.read_csv("preprocessed_data.csv")

def main():

    df=load_data()

    page=st.sidebar.radio("📂 Select Page",[
    "📊 Portfolio Dashboard",
    "⚙ Rule-Based Investment Mix"
    ])

    if page=="📊 Portfolio Dashboard":
        st.title("Dashboard Working ✅")

    if page=="⚙ Rule-Based Investment Mix":
        st.title("Calculator Working ✅")
# =====================================================
    # PAGE 1 — PORTFOLIO DASHBOARD
    # =====================================================
    if page=="📊 Portfolio Dashboard":

        st.subheader("📊 Crypto Portfolio Dashboard")

        cryptos=sorted(df["Crypto"].unique())
        selected_crypto=st.multiselect("Select Cryptos",cryptos,default=cryptos)

        filtered=df[df["Crypto"].isin(selected_crypto)]

        latest_prices=filtered.sort_values("Date").groupby("Crypto").tail(1)

        total_assets=len(latest_prices)
        avg_price=latest_prices["Close"].mean()
        total_volume=latest_prices["Volume"].sum()

        col1,col2,col3=st.columns(3)

        col1.metric("💰 Total Assets",total_assets)
        col2.metric("📈 Avg Price",f"${avg_price:,.2f}")
        col3.metric("🔄 Total Volume",f"{total_volume:,.0f}")

        st.divider()

        # PRICE TREND
        st.subheader("📈 Price Trend")
        fig_trend=px.line(filtered,x="Date",y="Close",color="Crypto")
        st.plotly_chart(fig_trend,use_container_width=True)

        # ALLOCATION
        st.subheader("🥧 Portfolio Allocation")
        fig_pie=px.pie(latest_prices,names="Crypto",values="Close",hole=0.4)
        st.plotly_chart(fig_pie,use_container_width=True)

        # VOLATILITY
        st.subheader("📊 Volatility")
        volatility=filtered.groupby("Crypto")["Close"].std().reset_index()
        fig_vol=px.bar(volatility,x="Crypto",y="Close",color="Crypto")
        st.plotly_chart(fig_vol,use_container_width=True)

        # RETURNS
        st.subheader("📉 Return Analysis")
        returns=filtered.groupby("Crypto").apply(
            lambda x:(x["Close"].iloc[-1]-x["Close"].iloc[0])/x["Close"].iloc[0]*100
        ).reset_index(name="Return %")

        fig_return=px.bar(returns,x="Crypto",y="Return %",color="Crypto")
        st.plotly_chart(fig_return,use_container_width=True)

        st.subheader("📄 Data Preview")
        st.dataframe(filtered.sort_values("Date",ascending=False),use_container_width=True)


    # =====================================================
    # PAGE 2 — RULE-BASED MIX
    # =====================================================
    if page=="⚙ Rule-Based Investment Mix":

        st.subheader("⚙ Rule-Based Investment Mix Calculator")

        risk_level=st.selectbox("Select Risk Level",["Low","Medium","High"])

        returns=df.groupby("Crypto").apply(
            lambda x:(x["Close"].iloc[-1]-x["Close"].iloc[0])/x["Close"].iloc[0]
        ).reset_index(name="Return")

        volatility=df.groupby("Crypto")["Close"].std().reset_index(name="Volatility")

        metrics=returns.merge(volatility,on="Crypto")

        metrics["Return_norm"]=metrics["Return"]/metrics["Return"].max()
        metrics["Vol_norm"]=metrics["Volatility"]/metrics["Volatility"].max()

        if risk_level=="Low":
            metrics["Score"]=0.7*(1-metrics["Vol_norm"])+0.3*(metrics["Return_norm"])
        elif risk_level=="Medium":
            metrics["Score"]=0.5*(1-metrics["Vol_norm"])+0.5*(metrics["Return_norm"])
        else:
            metrics["Score"]=0.3*(1-metrics["Vol_norm"])+0.7*(metrics["Return_norm"])

        metrics["Allocation %"]=metrics["Score"]/metrics["Score"].sum()*100

        st.subheader("📊 Recommended Allocation")
        st.dataframe(metrics[["Crypto","Allocation %"]],use_container_width=True)

        fig_mix=px.pie(metrics,names="Crypto",values="Allocation %",hole=0.4)
        st.plotly_chart(fig_mix,use_container_width=True)

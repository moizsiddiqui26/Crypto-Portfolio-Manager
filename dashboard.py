# =========================================================
# CRYPTO PORTFOLIO MANAGER - DASHBOARD
# Uses: preprocessed_data.csv
# =========================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    df=pd.read_csv("preprocessed_data.csv")
    df["Date"]=pd.to_datetime(df["Date"])
    return df

df=load_data()

# ---------------- SIDEBAR FILTER ----------------
st.sidebar.header("📊 Portfolio Controls")

cryptos=sorted(df["Crypto"].unique())
selected_crypto=st.sidebar.multiselect("Select Cryptos",cryptos,default=cryptos)

filtered=df[df["Crypto"].isin(selected_crypto)]

# ---------------- SUMMARY CALCULATIONS ----------------
latest_prices=filtered.sort_values("Date").groupby("Crypto").tail(1)

total_assets=len(latest_prices)
avg_price=latest_prices["Close"].mean()
total_volume=latest_prices["Volume"].sum()

# ---------------- SUMMARY CARDS ----------------
col1,col2,col3=st.columns(3)

col1.metric("💰 Total Assets",total_assets)
col2.metric("📈 Avg Price",f"${avg_price:,.2f}")
col3.metric("🔄 Total Volume",f"{total_volume:,.0f}")

st.divider()

# =========================================================
# PRICE TREND CHART
# =========================================================
st.subheader("📈 Price Trend")

fig_trend=px.line(
    filtered,
    x="Date",
    y="Close",
    color="Crypto",
    title="Crypto Closing Price Over Time"
)

st.plotly_chart(fig_trend,use_container_width=True)

# =========================================================
# PORTFOLIO ALLOCATION (BASED ON LAST PRICE)
# =========================================================
st.subheader("🥧 Portfolio Allocation")

fig_pie=px.pie(
    latest_prices,
    names="Crypto",
    values="Close",
    hole=0.4
)

st.plotly_chart(fig_pie,use_container_width=True)

# =========================================================
# VOLATILITY ANALYSIS
# =========================================================
st.subheader("📊 Volatility Analysis")

volatility=filtered.groupby("Crypto")["Close"].std().reset_index()
volatility.columns=["Crypto","Volatility"]

fig_vol=px.bar(volatility,x="Crypto",y="Volatility",color="Crypto")

st.plotly_chart(fig_vol,use_container_width=True)

# =========================================================
# RETURN ANALYSIS
# =========================================================
st.subheader("📉 Return Analysis")

returns=filtered.groupby("Crypto").apply(
    lambda x:(x["Close"].iloc[-1]-x["Close"].iloc[0])/x["Close"].iloc[0]*100
).reset_index(name="Return %")

fig_return=px.bar(returns,x="Crypto",y="Return %",color="Crypto")

st.plotly_chart(fig_return,use_container_width=True)

# =========================================================
# DATA TABLE
# =========================================================
st.subheader("📄 Raw Data Preview")
st.dataframe(filtered.sort_values("Date",ascending=False),use_container_width=True)

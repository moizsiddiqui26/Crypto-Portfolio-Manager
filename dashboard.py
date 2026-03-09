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
if page=="📊 Portfolio Dashboard":
# ---------------- PAGE SELECTOR ----------------
page=st.sidebar.radio("📂 Select Page",[
"📊 Portfolio Dashboard",
"⚙ Rule-Based Investment Mix"
])
    # (PASTE YOUR CURRENT DASHBOARD CODE HERE)
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
# =========================================================
# RULE-BASED INVESTMENT MIX PAGE
# =========================================================

if page=="⚙ Rule-Based Investment Mix":

    st.title("⚙ Rule-Based Investment Mix Calculator")

    st.write("""
Rule-based method mixes investments using volatility and return.
Goal → Best return with controlled risk.
""")

    # ---------------- RISK LEVEL SELECT ----------------
    risk_level=st.selectbox("Select Risk Level",["Low","Medium","High"])

    # ---------------- CALCULATE METRICS ----------------
    returns=df.groupby("Crypto").apply(
        lambda x:(x["Close"].iloc[-1]-x["Close"].iloc[0])/x["Close"].iloc[0]
    ).reset_index(name="Return")

    volatility=df.groupby("Crypto")["Close"].std().reset_index(name="Volatility")

    metrics=returns.merge(volatility,on="Crypto")

    # Normalize values
    metrics["Return_norm"]=metrics["Return"]/metrics["Return"].max()
    metrics["Vol_norm"]=metrics["Volatility"]/metrics["Volatility"].max()

    # ---------------- RULE-BASED LOGIC ----------------
    if risk_level=="Low":
        metrics["Score"]=0.7*(1-metrics["Vol_norm"])+0.3*(metrics["Return_norm"])

    elif risk_level=="Medium":
        metrics["Score"]=0.5*(1-metrics["Vol_norm"])+0.5*(metrics["Return_norm"])

    else:
        metrics["Score"]=0.3*(1-metrics["Vol_norm"])+0.7*(metrics["Return_norm"])

    # Convert score to allocation %
    metrics["Allocation %"]=metrics["Score"]/metrics["Score"].sum()*100

    st.subheader("📊 Recommended Allocation")
    st.dataframe(metrics[["Crypto","Allocation %"]])

    # ---------------- PIE CHART ----------------
    import plotly.express as px

    fig=px.pie(metrics,names="Crypto",values="Allocation %",hole=0.4,
               title="Recommended Portfolio Mix")

    st.plotly_chart(fig,use_container_width=True)

    # ---------------- SAMPLE TEST EXPLANATION ----------------
    st.subheader("📌 Rule Explanation")

    st.write("""
• Low Risk → More weight to low volatility coins  
• Medium Risk → Balanced approach  
• High Risk → More weight to high return coins  

Tested using historical price dataset.
""")

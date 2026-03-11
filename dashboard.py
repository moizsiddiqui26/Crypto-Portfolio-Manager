# =====================================================
# CRYPTO PORTFOLIO MANAGER - FINAL DASHBOARD (UPDATED)
# Predictor moved inside Risk Checker
# =====================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import json,os
from sklearn.linear_model import LinearRegression
from risk_predictor import run_risk_checks
from email_alert import send_alert


# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    df=pd.read_csv("preprocessed_data.csv")
    df["Date"]=pd.to_datetime(df["Date"])
    return df


# =====================================================
# MAIN FUNCTION
# =====================================================
def main():

    df=load_data()

    page=st.sidebar.radio("Navigation",[
    "📊 Dashboard",
    "⚙ Investment Mix Calculator",
    "⚠ Risk Checker",
    "👤 User Profile"
    ])


# =================================================
# DASHBOARD PAGE (EDA ONLY)
# =================================================
    if page=="📊 Dashboard":

        st.header("📊 Portfolio Dashboard + EDA")

        cryptos=sorted(df["Crypto"].unique())
        sel=st.multiselect("Select Crypto",cryptos,default=cryptos)

        f=df[df["Crypto"].isin(sel)]
        latest=f.sort_values("Date").groupby("Crypto").tail(1)

        # METRICS
        col1,col2,col3=st.columns(3)
        col1.metric("Assets",len(latest))
        col2.metric("Avg Price",f"${latest.Close.mean():,.2f}")
        col3.metric("Volume",f"{latest.Volume.sum():,.0f}")

        st.divider()

        # PRICE TREND
        st.subheader("📈 Price Trend")
        st.plotly_chart(px.line(f,x="Date",y="Close",color="Crypto"),
                        use_container_width=True)

        # VOLATILITY
        st.subheader("📊 Volatility")
        volatility=f.groupby("Crypto")["Close"].std().reset_index()
        st.plotly_chart(px.bar(volatility,x="Crypto",y="Close",color="Crypto"),
                        use_container_width=True)

        # RETURNS
        st.subheader("📉 Return %")
        returns=f.groupby("Crypto").apply(
            lambda x:(x.Close.iloc[-1]-x.Close.iloc[0])/x.Close.iloc[0]*100
        ).reset_index(name="Return %")

        st.plotly_chart(px.bar(returns,x="Crypto",y="Return %",color="Crypto"),
                        use_container_width=True)

        # MOVING AVERAGE
        st.subheader("📈 Moving Average")

        f["MA20"]=f.groupby("Crypto")["Close"].transform(lambda x:x.rolling(20).mean())

        st.plotly_chart(px.line(f,x="Date",y="MA20",color="Crypto"),
                        use_container_width=True)

        # BOXPLOT
        st.subheader("📦 Distribution")
        st.plotly_chart(px.box(f,x="Crypto",y="Close",color="Crypto"),
                        use_container_width=True)

        # HEATMAP
        st.subheader("🔥 Correlation Heatmap")

        pivot=f.pivot(index="Date",columns="Crypto",values="Close")
        corr=pivot.corr()

        st.plotly_chart(px.imshow(corr,text_auto=True),
                        use_container_width=True)


# =================================================
# MIX CALCULATOR
# =================================================
    if page=="⚙ Investment Mix Calculator":

        st.header("Investment Mix Calculator")

        amount=st.number_input("Amount to Invest",value=1000.0)
        risk=st.selectbox("Risk Level",["Low","Medium","High"])

        returns=df.groupby("Crypto").apply(
            lambda x:(x.Close.iloc[-1]-x.Close.iloc[0])/x.Close.iloc[0]
        ).reset_index(name="Return")

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
        st.plotly_chart(px.pie(m,names="Crypto",values="Investment"),
                        use_container_width=True)

        st.download_button("Download CSV",m.to_csv(index=False),"investment_mix.csv")


# =================================================
# RISK CHECKER + PREDICTOR
# =================================================
    if page=="⚠ Risk Checker":

        st.header("⚠ Risk Checker + Predictor")

        if st.button("Run Risk Check"):
            result=run_risk_checks(df)
            st.dataframe(result)

            if (result["Risk"]=="High").any():
                send_alert(result)
                st.warning("High risk detected. Email sent.")

        st.divider()

        # ================= PREDICTOR =================
        st.subheader("🔮 Profit Prediction")

        cryptos=sorted(df["Crypto"].unique())

        col1,col2,col3=st.columns(3)

        with col1:
            pred_coin=st.selectbox("Crypto",cryptos)

        with col2:
            invest_amount=st.number_input("Investment Amount ($)",min_value=1.0,value=1000.0)

        with col3:
            days=st.number_input("Days",min_value=1,value=7)

        coin_df=df[df["Crypto"]==pred_coin].sort_values("Date")

        coin_df["t"]=range(len(coin_df))
        x=coin_df["t"].values.reshape(-1,1)
        y=coin_df["Close"].values

        model=LinearRegression()
        model.fit(x,y)

        future_t=np.arange(len(coin_df),len(coin_df)+days).reshape(-1,1)
        future_pred=model.predict(future_t)

        future_dates=pd.date_range(
            coin_df["Date"].iloc[-1]+pd.Timedelta(days=1),
            periods=days
        )

        current_price=coin_df["Close"].iloc[-1]
        expected_price=future_pred[-1]

        units=invest_amount/current_price
        expected_value=units*expected_price
        profit=expected_value-invest_amount
        profit_pct=(profit/invest_amount)*100

        col1,col2,col3=st.columns(3)
        col1.metric("Expected Amount",f"${expected_value:,.2f}")
        col2.metric("Expected Profit",f"${profit:,.2f}")
        col3.metric("Profit %",f"{profit_pct:.2f}%")

        fig=go.Figure()
        fig.add_trace(go.Scatter(x=coin_df["Date"],y=coin_df["Close"],name="Actual"))
        fig.add_trace(go.Scatter(x=future_dates,y=future_pred,name="Predicted"))

        st.plotly_chart(fig,use_container_width=True)


# =================================================
# USER PROFILE (SAME)
# =================================================
    if page=="👤 User Profile":

        st.info("User Profile remains same (use your latest version)")

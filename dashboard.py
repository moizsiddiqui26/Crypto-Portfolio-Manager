# =====================================================
# CRYPTO PORTFOLIO MANAGER - FINAL DASHBOARD (FULL)
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
# DASHBOARD PAGE (FULL EDA + PREDICTION)
# =================================================
    if page=="📊 Dashboard":

        st.header("📊 Portfolio Dashboard + EDA + Prediction")

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
        st.subheader("📊 Volatility Analysis")
        volatility=f.groupby("Crypto")["Close"].std().reset_index()
        st.plotly_chart(px.bar(volatility,x="Crypto",y="Close",
                        title="Volatility (Std Dev)",color="Crypto"),
                        use_container_width=True)

        # RETURNS
        st.subheader("📉 Return % Analysis")
        returns=f.groupby("Crypto").apply(
            lambda x:(x.Close.iloc[-1]-x.Close.iloc[0])/x.Close.iloc[0]*100
        ).reset_index(name="Return %")

        st.plotly_chart(px.bar(returns,x="Crypto",y="Return %",
                        color="Crypto"),
                        use_container_width=True)

        # MOVING AVERAGE
        st.subheader("📈 Moving Average Trend")
        f["MA20"]=f.groupby("Crypto")["Close"].transform(lambda x:x.rolling(20).mean())

        st.plotly_chart(px.line(f,x="Date",y="MA20",color="Crypto"),
                        use_container_width=True)

        # BOXPLOT
        st.subheader("📦 Price Distribution")
        st.plotly_chart(px.box(f,x="Crypto",y="Close",color="Crypto"),
                        use_container_width=True)

        # CORRELATION
        st.subheader("🔥 Correlation Heatmap")
        pivot=f.pivot(index="Date",columns="Crypto",values="Close")
        st.plotly_chart(px.imshow(pivot.corr(),text_auto=True),
                        use_container_width=True)

# =================================================
# 🔮 PRICE PREDICTION (NEW)
# =================================================
        st.subheader("🔮 Price Prediction (Next 7 Days)")

        pred_coin=st.selectbox("Select Crypto for Prediction",cryptos)

        coin_df=df[df["Crypto"]==pred_coin].sort_values("Date")

        coin_df["t"]=range(len(coin_df))

        x=coin_df["t"].values.reshape(-1,1)
        y=coin_df["Close"].values

        model=LinearRegression()
        model.fit(x,y)

        future_t=np.arange(len(coin_df),len(coin_df)+7).reshape(-1,1)
        future_pred=model.predict(future_t)

        future_dates=pd.date_range(
            coin_df["Date"].iloc[-1]+pd.Timedelta(days=1),
            periods=7
        )

        pred_df=pd.DataFrame({
            "Date":future_dates,
            "Predicted Price":future_pred
        })

        fig=go.Figure()
        fig.add_trace(go.Scatter(x=coin_df["Date"],y=coin_df["Close"],
                                 mode="lines",name="Actual"))
        fig.add_trace(go.Scatter(x=pred_df["Date"],y=pred_df["Predicted Price"],
                                 mode="lines+markers",name="Predicted"))

        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pred_df,use_container_width=True)


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
# RISK CHECKER
# =================================================
    if page=="⚠ Risk Checker":

        st.header("Risk Checker + Predictor")

        if st.button("Run Risk Check"):
            result=run_risk_checks(df)
            st.dataframe(result)

            if (result["Risk"]=="High").any():
                send_alert(result)
                st.warning("High risk detected. Email sent.")


# =================================================
# USER PROFILE
# =================================================
    if page=="👤 User Profile":

        st.header("👤 User Profile")

        user=st.session_state.user
        HOLDINGS_FILE="holdings.json"

        # SAFE LOAD
        if os.path.exists(HOLDINGS_FILE):
            try:
                with open(HOLDINGS_FILE,"r") as f:
                    all_hold=json.load(f)
            except:
                all_hold={}
        else:
            all_hold={}

        if user not in all_hold:
            all_hold[user]=[]

        hold=all_hold[user]

        st.subheader("📊 Investment Overview")

        if hold:

            latest=df.sort_values("Date").groupby("Crypto").tail(1)

            rows=[]
            total_invested=0
            total_current=0

            fixed_hold=[]

            if isinstance(hold,dict):
                for c,a in hold.items():
                    fixed_hold.append({
                        "crypto":c,
                        "amount":a,
                        "date":str(df["Date"].min().date())
                    })
            else:
                fixed_hold=hold

            for h in fixed_hold:

                coin=h["crypto"]
                invest_amt=h["amount"]
                invest_date=pd.to_datetime(h["date"])

                past=df[(df["Crypto"]==coin)&(df["Date"]<=invest_date)].tail(1)

                past_price=float(past["Close"]) if not past.empty else 0
                current_price=float(latest[latest["Crypto"]==coin]["Close"])

                units=invest_amt/past_price if past_price>0 else 0
                current_value=units*current_price
                profit=((current_value-invest_amt)/invest_amt*100) if invest_amt>0 else 0

                total_invested+=invest_amt
                total_current+=current_value

                rows.append([
                    coin,invest_date.date(),invest_amt,past_price,
                    current_price,units,current_value,profit
                ])

            table=pd.DataFrame(rows,columns=[
                "Crypto","Invest Date","Invested ($)",
                "Buy Price","Current Price","Units",
                "Current Value ($)","Profit %"
            ])

            col1,col2,col3=st.columns(3)
            col1.metric("Total Invested",f"${total_invested:,.2f}")
            col2.metric("Current Value",f"${total_current:,.2f}")
            col3.metric("Profit %",
                        f"{((total_current-total_invested)/total_invested*100):.2f}%")

            st.dataframe(table,use_container_width=True)

            st.plotly_chart(px.pie(table,names="Crypto",values="Current Value ($)"),
                            use_container_width=True)

        else:
            st.info("No investments added yet")

        st.divider()

        st.subheader("➕ Add Investment")

        cryptos=sorted(df["Crypto"].unique())

        col1,col2,col3=st.columns(3)

        with col1:
            coin=st.selectbox("Crypto Currency",cryptos)

        with col2:
            invest_amt=st.number_input("Amount Invested ($)",min_value=0.0)

        with col3:
            invest_date=st.date_input("Investment Date")

        if st.button("Save Investment"):

            hold.append({
                "crypto":coin,
                "amount":invest_amt,
                "date":str(invest_date)
            })

            all_hold[user]=hold

            with open(HOLDINGS_FILE,"w") as f:
                json.dump(all_hold,f)

            st.success("Investment Saved")
            st.rerun()

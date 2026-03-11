# =====================================================
# FINAL DASHBOARD (ADVANCED EDA + MIX LEVEL + PROFILE)
# =====================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np,json,os,requests
from sklearn.linear_model import LinearRegression
from risk_predictor import run_risk_checks
from email_alert import send_alert


# ---------------- LIVE DATA ----------------
@st.cache_data(ttl=300)
def load_data():

    coins={"BTC":"bitcoin","ETH":"ethereum","BNB":"binancecoin","SOL":"solana","ADA":"cardano"}

    all_df=[]

    for c,id in coins.items():

        url=f"https://api.coingecko.com/api/v3/coins/{id}/market_chart"
        data=requests.get(url,params={"vs_currency":"usd","days":120}).json()

        temp=pd.DataFrame(data["prices"],columns=["timestamp","Close"])
        temp["Date"]=pd.to_datetime(temp["timestamp"],unit="ms")
        temp["Crypto"]=c

        all_df.append(temp[["Date","Crypto","Close"]])

    return pd.concat(all_df)


# =====================================================
def main():

    df=load_data()

    page=st.sidebar.radio("Navigation",
    ["📊 Dashboard","⚙ Investment Mix Calculator","⚠ Risk Checker","👤 User Profile"])


# =====================================================
# 📊 DASHBOARD (ADVANCED EDA)
# =====================================================
    if page=="📊 Dashboard":

        st.header("📊 Advanced Crypto EDA")

        cryptos=df["Crypto"].unique()
        sel=st.multiselect("Select Crypto",cryptos,default=cryptos)

        f=df[df["Crypto"].isin(sel)]

        # PRICE TREND
        st.subheader("📈 Price Trend")
        st.plotly_chart(px.line(f,x="Date",y="Close",color="Crypto"),
                        use_container_width=True)

        # DAILY RETURNS
        st.subheader("📉 Daily Returns")

        f["Return"]=f.groupby("Crypto")["Close"].pct_change()

        st.plotly_chart(px.line(f,x="Date",y="Return",color="Crypto"),
                        use_container_width=True)

        # VOLATILITY ROLLING
        st.subheader("📊 Rolling Volatility")

        f["Volatility"]=f.groupby("Crypto")["Return"].transform(lambda x:x.rolling(7).std())

        st.plotly_chart(px.line(f,x="Date",y="Volatility",color="Crypto"),
                        use_container_width=True)

        # DISTRIBUTION HISTOGRAM
        st.subheader("📦 Return Distribution")

        st.plotly_chart(px.histogram(f,x="Return",color="Crypto",nbins=50),
                        use_container_width=True)

        # CORRELATION HEATMAP
        st.subheader("🔥 Correlation Heatmap")

        pivot=f.pivot(index="Date",columns="Crypto",values="Close")
        corr=pivot.pct_change().corr()

        st.plotly_chart(px.imshow(corr,text_auto=True),
                        use_container_width=True)


# =====================================================
# ⚙ MIX CALCULATOR (LEVEL ADDED)
# =====================================================
    if page=="⚙ Investment Mix Calculator":

        st.header("⚙ Investment Mix Calculator")

        amount=st.number_input("Amount to Invest ($)",value=1000.0)

        level=st.selectbox("Select Investment Level",
        ["Low Risk","Medium Risk","High Risk"])

        returns=df.groupby("Crypto").apply(lambda x:(x.Close.iloc[-1]-x.Close.iloc[0])/x.Close.iloc[0]).reset_index(name="Return")
        vol=df.groupby("Crypto")["Close"].std().reset_index(name="Vol")

        m=returns.merge(vol,on="Crypto")

        if level=="Low Risk":
            m["Score"]=(1/m["Vol"])
        elif level=="Medium Risk":
            m["Score"]=m["Return"]/m["Vol"]
        else:
            m["Score"]=m["Return"]

        m["Allocation %"]=m.Score/m.Score.sum()*100
        m["Investment"]=m["Allocation %"]/100*amount

        st.dataframe(m)

        st.plotly_chart(px.pie(m,names="Crypto",values="Investment"),
                        use_container_width=True)

        st.download_button("Download CSV",m.to_csv(index=False),"mix.csv")


# =====================================================
# ⚠ RISK CHECKER + PREDICTOR
# =====================================================
    if page=="⚠ Risk Checker":

        if st.button("Run Risk Check"):
            result=run_risk_checks(df)
            st.dataframe(result)

            send_alert(result,st.session_state.email)

        st.subheader("🔮 Prediction")

        coin=st.selectbox("Crypto",df["Crypto"].unique())
        days=st.slider("Days",1,30,7)

        coin_df=df[df["Crypto"]==coin].sort_values("Date")

        coin_df["t"]=range(len(coin_df))
        model=LinearRegression().fit(coin_df[["t"]],coin_df["Close"])

        future_t=np.arange(len(coin_df),len(coin_df)+days)
        future=model.predict(future_t.reshape(-1,1))

        future_dates=pd.date_range(coin_df["Date"].iloc[-1],periods=days+1)[1:]

        fig=go.Figure()
        fig.add_trace(go.Scatter(x=coin_df["Date"],y=coin_df["Close"],name="Actual"))
        fig.add_trace(go.Scatter(x=future_dates,y=future,name="Predicted"))

        st.plotly_chart(fig,use_container_width=True)


# =====================================================
# 👤 USER PROFILE (FINAL)
# =====================================================
    if page=="👤 User Profile":

        email=st.session_state.email
        file="holdings.json"

        if os.path.exists(file):
            with open(file,"r") as f: data=json.load(f)
        else: data={}

        if email not in data: data[email]=[]

        hold=data[email]

        st.subheader("➕ Add Investment")

        coin=st.selectbox("Crypto",df["Crypto"].unique())
        amt=st.number_input("Amount",min_value=0.0)
        date=st.date_input("Date")

        if st.button("Save"):
            hold.append({"crypto":coin,"amount":amt,"date":str(date)})
            data[email]=hold
            with open(file,"w") as f: json.dump(data,f)
            st.success("Saved")

        if hold:

            latest=df.sort_values("Date").groupby("Crypto").tail(1)

            rows=[]

            for h in hold:

                coin=h["crypto"]
                amt=h["amount"]

                price=float(latest[latest["Crypto"]==coin]["Close"])

                units=amt/price if price>0 else 0
                current_val=units*price
                pct=((current_val-amt)/amt)*100 if amt>0 else 0

                rows.append([coin,amt,current_val,pct])

            table=pd.DataFrame(rows,columns=["Crypto","Invested","Current Value","% Change"])

            st.dataframe(table)

            st.plotly_chart(px.pie(table,names="Crypto",values="Current Value"),
                            use_container_width=True)

            st.plotly_chart(px.bar(table,x="Crypto",y="% Change",color="Crypto"),
                            use_container_width=True)

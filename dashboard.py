import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np,json,os,requests
from sklearn.linear_model import LinearRegression
from risk_predictor import run_risk_checks
from email_alert import send_alert

@st.cache_data(ttl=300)
def load_data():
    coins={"BTC":"bitcoin","ETH":"ethereum","BNB":"binancecoin","SOL":"solana","ADA":"cardano"}
    all_df=[]
    for c,id in coins.items():
        url=f"https://api.coingecko.com/api/v3/coins/{id}/market_chart"
        data=requests.get(url,params={"vs_currency":"usd","days":90}).json()
        temp=pd.DataFrame(data["prices"],columns=["timestamp","Close"])
        temp["Date"]=pd.to_datetime(temp["timestamp"],unit="ms")
        temp["Crypto"]=c
        all_df.append(temp[["Date","Crypto","Close"]])
    return pd.concat(all_df)

def main():
    df=load_data()

    page=st.sidebar.radio("Navigation",[
    "📊 Dashboard","⚙ Investment Mix Calculator","⚠ Risk Checker","👤 User Profile"
    ])

# ================= DASHBOARD =================
    if page=="📊 Dashboard":

        st.header("📊 Live Crypto Dashboard")

        cryptos=df["Crypto"].unique()
        sel=st.multiselect("Select Crypto",cryptos,default=cryptos)

        f=df[df["Crypto"].isin(sel)]

        st.plotly_chart(px.line(f,x="Date",y="Close",color="Crypto"),
                        use_container_width=True)

        vol=f.groupby("Crypto")["Close"].std().reset_index()
        st.plotly_chart(px.bar(vol,x="Crypto",y="Close",color="Crypto"),
                        use_container_width=True)

# ================= MIX =================
    if page=="⚙ Investment Mix Calculator":

        amount=st.number_input("Amount",value=1000.0)
        returns=df.groupby("Crypto").apply(lambda x:(x.Close.iloc[-1]-x.Close.iloc[0])/x.Close.iloc[0]).reset_index(name="Return")
        vol=df.groupby("Crypto")["Close"].std().reset_index(name="Vol")

        m=returns.merge(vol,on="Crypto")
        m["Score"]=m.Return/m.Vol
        m["Allocation"]=m.Score/m.Score.sum()*amount

        st.dataframe(m)
        st.download_button("CSV",m.to_csv(index=False),"mix.csv")

# ================= RISK =================
    if page=="⚠ Risk Checker":

        if st.button("Run Risk Check"):
            result=run_risk_checks(df)
            st.dataframe(result)
            send_alert(result,st.session_state.email)

# ================= PROFILE =================
    if page=="👤 User Profile":

        email=st.session_state.email
        file="holdings.json"

        if os.path.exists(file):
            with open(file,"r") as f: data=json.load(f)
        else: data={}

        if email not in data: data[email]=[]

        hold=data[email]

        st.subheader("Add Investment")

        coin=st.selectbox("Crypto",df["Crypto"].unique())
        amt=st.number_input("Amount",min_value=0.0)
        date=st.date_input("Date")

        if st.button("Save"):
            hold.append({"crypto":coin,"amount":amt,"date":str(date)})
            data[email]=hold
            with open(file,"w") as f: json.dump(data,f)
            st.success("Saved")

        if hold:
            table=pd.DataFrame(hold)
            st.dataframe(table)

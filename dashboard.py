import streamlit as st
import pandas as pd
import plotly.express as px
import json,os
from risk_predictor import run_risk_checks
from email_alert import send_alert

@st.cache_data
def load_data():
    df=pd.read_csv("preprocessed_data.csv")
    df["Date"]=pd.to_datetime(df["Date"])
    return df

def main():

    df=load_data()

    page=st.sidebar.radio("Navigation",[
    "📊 Dashboard",
    "⚙ Investment Mix Calculator",
    "⚠ Risk Checker",
    "👤 User Profile"
    ])

    # ================= DASHBOARD =================
    if page=="📊 Dashboard":

        st.header("Portfolio Dashboard")

        cryptos=sorted(df["Crypto"].unique())
        sel=st.multiselect("Select Crypto",cryptos,default=cryptos)

        f=df[df["Crypto"].isin(sel)]
        latest=f.sort_values("Date").groupby("Crypto").tail(1)

        col1,col2,col3=st.columns(3)
        col1.metric("Assets",len(latest))
        col2.metric("Avg Price",f"${latest.Close.mean():,.2f}")
        col3.metric("Volume",f"{latest.Volume.sum():,.0f}")

        st.plotly_chart(px.line(f,x="Date",y="Close",color="Crypto"),use_container_width=True)


    # ================= MIX CALCULATOR =================
    if page=="⚙ Investment Mix Calculator":

        st.header("Investment Mix Calculator")

        amount=st.number_input("Amount to Invest",value=1000.0)
        risk=st.selectbox("Risk Level",["Low","Medium","High"])

        returns=df.groupby("Crypto").apply(lambda x:(x.Close.iloc[-1]-x.Close.iloc[0])/x.Close.iloc[0]).reset_index(name="Return")
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

        st.plotly_chart(px.pie(m,names="Crypto",values="Investment"),use_container_width=True)

        st.download_button("Download CSV",m.to_csv(index=False),"investment_mix.csv")


    # ================= RISK CHECKER =================
    if page=="⚠ Risk Checker":

        st.header("Risk Checker + Predictor")

        if st.button("Run Risk Check"):
            result=run_risk_checks(df)
            st.dataframe(result)

            if (result["Risk"]=="High").any():
                send_alert(result)
                st.warning("High risk detected. Email sent.")


    # ================= USER PROFILE =================
    if page=="👤 User Profile":

        st.header("User Profile")

        user=st.session_state.user
        HOLDINGS_FILE="holdings.json"

        if os.path.exists(HOLDINGS_FILE):
            with open(HOLDINGS_FILE,"r") as f: all_hold=json.load(f)
        else: all_hold={}

        if user not in all_hold: all_hold[user]={}
        hold=all_hold[user]

        st.subheader("➕ Add Investment")

        cryptos=sorted(df["Crypto"].unique())
        coin=st.selectbox("Crypto Currency",cryptos)
        invest=st.number_input("Amount Invested ($)",min_value=0.0)

        if st.button("Save Investment"):
            hold[coin]=hold.get(coin,0)+invest
            all_hold[user]=hold

            with open(HOLDINGS_FILE,"w") as f: json.dump(all_hold,f)

            st.success("Investment Saved")

        st.divider()

        st.subheader("📊 Your Holdings")

        if hold:

            latest=df.sort_values("Date").groupby("Crypto").tail(1)

            rows=[]
            total=0

            for c,a in hold.items():
                price=float(latest[latest.Crypto==c]["Close"])
                val=a/price if price>0 else 0
                total+=a
                rows.append([c,a,price,val])

            table=pd.DataFrame(rows,columns=["Crypto","Amount Invested","Price","Units"])

            st.metric("Total Invested",f"${total:,.2f}")
            st.dataframe(table,use_container_width=True)

            st.plotly_chart(px.pie(table,names="Crypto",values="Amount Invested"),
                            use_container_width=True)

        else:
            st.info("No investments yet")

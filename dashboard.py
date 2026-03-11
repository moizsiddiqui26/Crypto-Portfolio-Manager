# =====================================================
# CRYPTO PORTFOLIO MANAGER - FINAL DASHBOARD
# =====================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import json,os
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
    # USER PROFILE (UPDATED STRUCTURE)
    # =================================================
    if page=="👤 User Profile":

        st.header("👤 User Profile")

        user=st.session_state.user
        HOLDINGS_FILE="holdings.json"

        # LOAD HOLDINGS
        if os.path.exists(HOLDINGS_FILE):
            with open(HOLDINGS_FILE,"r") as f:
                all_hold=json.load(f)
        else:
            all_hold={}

        if user not in all_hold:
            all_hold[user]=[]

        hold=all_hold[user]

        # =================================================
        # TOP: INVESTMENT DETAILS + EDA
        # =================================================
        st.subheader("📊 Investment Overview")

        if hold:

            latest=df.sort_values("Date").groupby("Crypto").tail(1)

            rows=[]
            total_invested=0
            total_current=0

            for h in hold:

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
                    coin,
                    invest_date.date(),
                    invest_amt,
                    past_price,
                    current_price,
                    units,
                    current_value,
                    profit
                ])

            table=pd.DataFrame(rows,columns=[
                "Crypto","Invest Date","Invested ($)",
                "Buy Price","Current Price","Units",
                "Current Value ($)","Profit %"
            ])

            # -------- METRICS --------
            col1,col2,col3=st.columns(3)

            col1.metric("💰 Total Invested",f"${total_invested:,.2f}")
            col2.metric("📈 Current Value",f"${total_current:,.2f}")
            col3.metric("🚀 Profit %",
                        f"{((total_current-total_invested)/total_invested*100):.2f}%")

            st.divider()

            # -------- TABLE --------
            st.dataframe(table,use_container_width=True)

            # -------- PIE CHART --------
            st.subheader("📊 Portfolio Allocation")
            fig=px.pie(table,names="Crypto",values="Current Value ($)",hole=0.4)
            st.plotly_chart(fig,use_container_width=True)

            # -------- EDA PART --------
            st.subheader("📈 Investment EDA")

            eda=table.groupby("Crypto")["Profit %"].mean().reset_index()

            fig2=px.bar(eda,x="Crypto",y="Profit %",
                        title="Average Profit % by Crypto",
                        color="Crypto")

            st.plotly_chart(fig2,use_container_width=True)

        else:
            st.info("No investments added yet")

        st.divider()

        # =================================================
        # BOTTOM: ADD INVESTMENT FORM
        # =================================================
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


    # =================================================
    # OTHER PAGES SAME
    # =================================================
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

        st.plotly_chart(px.line(f,x="Date",y="Close",color="Crypto"),
                        use_container_width=True)


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

        st.plotly_chart(px.pie(m,names="Crypto",values="Investment"),
                        use_container_width=True)

        st.download_button("Download CSV",m.to_csv(index=False),"investment_mix.csv")


    if page=="⚠ Risk Checker":

        st.header("Risk Checker + Predictor")

        if st.button("Run Risk Check"):
            result=run_risk_checks(df)
            st.dataframe(result)

            if (result["Risk"]=="High").any():
                send_alert(result)
                st.warning("High risk detected. Email sent.")

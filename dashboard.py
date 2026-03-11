# =====================================================
# CRYPTO PORTFOLIO MANAGER - PREMIUM DASHBOARD (FINAL)
# =====================================================

import streamlit as st
import pandas as pd
import plotly.express as px

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

    page=st.sidebar.radio("📂 Navigation",[
    "📊 Portfolio Dashboard",
    "⚙ Investment Mix Calculator"
    ])

    # =================================================
    # DASHBOARD PAGE
    # =================================================
    if page=="📊 Portfolio Dashboard":

        st.header("📊 Portfolio Dashboard")

        cryptos=sorted(df["Crypto"].unique())
        selected_crypto=st.multiselect("Select Cryptos",cryptos,default=cryptos)

        filtered=df[df["Crypto"].isin(selected_crypto)]

        latest=filtered.sort_values("Date").groupby("Crypto").tail(1)

        col1,col2,col3=st.columns(3)

        col1.metric("💰 Assets",len(latest))
        col2.metric("📈 Avg Price",f"${latest['Close'].mean():,.2f}")
        col3.metric("🔄 Volume",f"{latest['Volume'].sum():,.0f}")

        st.divider()

        st.subheader("📈 Price Trend")
        fig=px.line(filtered,x="Date",y="Close",color="Crypto")
        st.plotly_chart(fig,use_container_width=True)

        st.subheader("🥧 Allocation")
        fig2=px.pie(latest,names="Crypto",values="Close",hole=.4)
        st.plotly_chart(fig2,use_container_width=True)


    # =================================================
    # MIX CALCULATOR PAGE
    # =================================================
    if page=="⚙ Investment Mix Calculator":

        st.header("⚙ Investment Mix Calculator")

        # ---------------- INPUT SECTION ----------------
        col1,col2=st.columns(2)

        with col1:
            amount=st.number_input("💰 Amount to Invest ($)",min_value=1.0,value=1000.0)

        with col2:
            risk=st.selectbox("📊 Select Risk Level",["Low","Medium","High"])

        st.divider()

        # ---------------- RULE CALCULATION ----------------
        returns=df.groupby("Crypto").apply(
            lambda x:(x["Close"].iloc[-1]-x["Close"].iloc[0])/x["Close"].iloc[0]
        ).reset_index(name="Return")

        vol=df.groupby("Crypto")["Close"].std().reset_index(name="Vol")

        m=returns.merge(vol,on="Crypto")

        # Normalize
        m["Return_n"]=m["Return"]/m["Return"].max()
        m["Vol_n"]=m["Vol"]/m["Vol"].max()

        # Rule Logic
        if risk=="Low":
            m["Score"]=.7*(1-m["Vol_n"])+.3*m["Return_n"]
        elif risk=="Medium":
            m["Score"]=.5*(1-m["Vol_n"])+.5*m["Return_n"]
        else:
            m["Score"]=.3*(1-m["Vol_n"])+.7*m["Return_n"]

        m["Allocation %"]=m["Score"]/m["Score"].sum()*100

        # ---------------- AMOUNT CALCULATION ----------------
        m["Investment Amount ($)"]=m["Allocation %"]/100*amount

        st.subheader("📊 Investment Breakdown")
        st.dataframe(m[["Crypto","Allocation %","Investment Amount ($)"]],
                     use_container_width=True)

        # ---------------- PIE CHART ----------------
        fig3=px.pie(m,names="Crypto",values="Investment Amount ($)",hole=.4,
                    title="Investment Distribution")

        st.plotly_chart(fig3,use_container_width=True)

        # ---------------- DOWNLOAD CSV ----------------
        csv=m[["Crypto","Allocation %","Investment Amount ($)"]].to_csv(index=False)

        st.download_button(
            label="⬇ Download Allocation CSV",
            data=csv,
            file_name="crypto_investment_mix.csv",
            mime="text/csv"
        )

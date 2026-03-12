import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np,json,os,time,requests
from sklearn.linear_model import LinearRegression
from risk_predictor import run_risk_checks
from email_alert import send_alert

@st.cache_data(ttl=300)
def load_data():

    coins={"BTC":"bitcoin","ETH":"ethereum","BNB":"binancecoin","SOL":"solana","ADA":"cardano"}

    all_df=[]

    for c,id in coins.items():

        url=f"https://api.coingecko.com/api/v3/coins/{id}/market_chart"

        try:

            r=requests.get(url,params={"vs_currency":"usd","days":120},timeout=10)

            if r.status_code!=200:
                continue

            data=r.json()

            if "prices" not in data:
                continue

            temp=pd.DataFrame(data["prices"],columns=["timestamp","Close"])
            temp["Date"]=pd.to_datetime(temp["timestamp"],unit="ms")
            temp["Crypto"]=c

            all_df.append(temp[["Date","Crypto","Close"]])

            time.sleep(1)

        except:
            continue

    if not all_df:
        st.error("Live data failed. Check internet.")
        return pd.DataFrame(columns=["Date","Crypto","Close"])

    return pd.concat(all_df)

def main():

    df=load_data()

    if df.empty:
        return

    page=st.sidebar.radio("Navigation",
    ["📊 Dashboard","⚙ Investment Mix Calculator","⚠ Risk Checker","👤 User Profile"])


# 📊 DASHBOARD 
    if page=="📊 Dashboard":

        st.header("📊 Advanced Crypto EDA")

        cryptos=df["Crypto"].unique()
        sel=st.multiselect("Select Crypto",cryptos,default=cryptos)

        f=df[df["Crypto"].isin(sel)]

        # PRICE TREND
        st.subheader("📈 Price Trend")
        st.plotly_chart(px.line(f,x="Date",y="Close",color="Crypto"),
                        use_container_width=True)

        # RETURNS
        st.subheader("📉 Daily Returns")

        f["Return"]=f.groupby("Crypto")["Close"].pct_change()

        st.plotly_chart(px.line(f,x="Date",y="Return",color="Crypto"),
                        use_container_width=True)

        # VOLATILITY
        st.subheader("📊 Rolling Volatility")

        f["Vol"]=f.groupby("Crypto")["Return"].transform(lambda x:x.rolling(7).std())

        st.plotly_chart(px.line(f,x="Date",y="Vol",color="Crypto"),
                        use_container_width=True)

        # HISTOGRAM
        st.subheader("📦 Return Distribution")

        st.plotly_chart(px.histogram(f,x="Return",color="Crypto",nbins=50),
                        use_container_width=True)

        # HEATMAP
        st.subheader("🔥 Correlation Heatmap")

        pivot=f.pivot(index="Date",columns="Crypto",values="Close")
        corr=pivot.pct_change().corr()

        st.plotly_chart(px.imshow(corr,text_auto=True),
                        use_container_width=True)


# ⚙ MIX CALCULATOR
    if page=="⚙ Investment Mix Calculator":

        st.header("⚙ Investment Mix Calculator")

        amount=st.number_input("Amount to Invest ($)",value=1000.0)

        level=st.selectbox("Select Investment Level",
        ["Low Risk","Medium Risk","High Risk"])

        returns=df.groupby("Crypto").apply(
        lambda x:(x.Close.iloc[-1]-x.Close.iloc[0])/x.Close.iloc[0]).reset_index(name="Return")

        vol=df.groupby("Crypto")["Close"].std().reset_index(name="Vol")

        m=returns.merge(vol,on="Crypto")

        if level=="Low Risk":
            m["Score"]=1/m["Vol"]
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


# ⚠ RISK CHECKER + PREDICTOR
        if page=="⚠ Risk Checker":

        if st.button("Run Risk Check"):
            result=run_risk_checks(df)
            st.dataframe(result)

            send_alert(result,st.session_state.email)

        # 🔮 INVESTMENT PREDICTION 
        
        st.subheader("🔮 Investment Prediction")

        cryptos=df["Crypto"].unique()

        col1,col2,col3=st.columns(3)

        with col1:
            coin=st.selectbox("Select Crypto",cryptos)

        with col2:
            invest_amount=st.number_input("Invested Amount ($)",min_value=1.0,value=1000.0)

        with col3:
            days=st.slider("Days to Predict",1,30,7)


        coin_df=df[df["Crypto"]==coin].sort_values("Date")

        # prepare regression
        coin_df["t"]=range(len(coin_df))
        model=LinearRegression().fit(coin_df[["t"]],coin_df["Close"])

        future_t=np.arange(len(coin_df),len(coin_df)+days)
        future_prices=model.predict(future_t.reshape(-1,1))

        future_dates=pd.date_range(coin_df["Date"].iloc[-1],periods=days+1)[1:]

        # current price
        current_price=coin_df["Close"].iloc[-1]

        # predicted future price (last day)
        future_price=future_prices[-1]

        # units purchased
        units=invest_amount/current_price

        # expected value
        expected_value=units*future_price

        # profit
        profit=expected_value-invest_amount
        profit_pct=(profit/invest_amount)*100


        # ================= OUTPUT =================

        col1,col2,col3=st.columns(3)

        col1.metric("📈 Future Price",f"${future_price:,.2f}")
        col2.metric("💰 Expected Amount",f"${expected_value:,.2f}")
        col3.metric("🚀 Profit %",f"{profit_pct:.2f}%")

        st.success(f"${invest_amount:,.0f} → ${expected_value:,.0f} in {days} days")


        # ================= CHART =================

        fig=go.Figure()

        fig.add_trace(go.Scatter(
        x=coin_df["Date"],
        y=coin_df["Close"],
        name="Actual"
        ))

        fig.add_trace(go.Scatter(
        x=future_dates,
        y=future_prices,
        name="Predicted"
        ))

        st.plotly_chart(fig,use_container_width=True)


# 👤 USER PROFILE 
    if page=="👤 User Profile":

        st.header("👤 User Profile")

        email=st.session_state.email
        file="holdings.json"

        # LOAD DATA
        if os.path.exists(file):
            with open(file,"r") as f:
                data=json.load(f)
        else:
            data={}

        if email not in data:
            data[email]=[]

        hold=data[email]

# ================= ADD INVESTMENT =================

        st.subheader("➕ Add Investment")

        coin=st.selectbox("Crypto",df["Crypto"].unique())
        amt=st.number_input("Amount ($)",min_value=0.0)
        date=st.date_input("Purchase Date")

        if st.button("Save Investment"):

            hold.append({
                "crypto":coin,
                "amount":amt,
                "date":str(date)
            })

            data[email]=hold

            with open(file,"w") as f:
                json.dump(data,f)

            st.success("Saved Successfully")

        if hold:

            st.subheader("📊 Investment Summary")

            latest=df.sort_values("Date").groupby("Crypto").tail(1)

            rows=[]

            for h in hold:

                coin=h["crypto"]
                amt=h["amount"]
                buy_date=pd.to_datetime(h["date"])

            # price at investment date
                past=df[(df["Crypto"]==coin)&(df["Date"]<=buy_date)].tail(1)

                buy_price=float(past["Close"]) if not past.empty else 0

            # current price
                current_price=float(latest[latest["Crypto"]==coin]["Close"])

            # quantity
                qty=amt/buy_price if buy_price>0 else 0

            # profit %
                profit_pct=((current_price-buy_price)/buy_price*100) if buy_price>0 else 0

                rows.append([
                    coin,
                    buy_date.date(),
                    amt,
                    qty,
                    buy_price,
                    current_price,
                    profit_pct
                ])

            table=pd.DataFrame(rows,columns=[
                "Currency",
                "Purchase Date",
                "Invested Amount ($)",
                "Quantity",
                "Price at Purchase ($)",
                "Current Price ($)",
                "Profit %"
            ])

            st.dataframe(table,use_container_width=True)



            st.subheader("📊 Portfolio Distribution")

            st.plotly_chart(px.pie(table,
                                   names="Currency",
                                   values="Invested Amount ($)"),
                            use_container_width=True)


            st.subheader("📈 Performance Comparison")

            fig=px.bar(table,
                       x="Currency",
                       y="Profit %",
                       color="Currency",
                       text="Profit %")

            fig.update_traces(texttemplate='%{text:.2f}%',textposition="outside")

            st.plotly_chart(fig,use_container_width=True)

        else:
            st.info("No investments added yet.")

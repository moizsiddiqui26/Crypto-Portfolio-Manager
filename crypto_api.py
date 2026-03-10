# =====================================================
# CRYPTO API (SAFE VERSION)
# =====================================================

import requests
import pandas as pd


def fetch_data():

    ids="bitcoin,ethereum,binancecoin,cardano,solana"

    url=f"https://api.coingecko.com/api/v3/simple/price?vs_currencies=usd&ids={ids}"

    try:
        res=requests.get(url,timeout=10).json()

        data=[]

        for c in ids.split(","):

            if c in res and "usd" in res[c]:

                data.append({
                    "Crypto":c.capitalize(),
                    "Price":res[c]["usd"]
                })

        # if API fails fallback demo data
        if len(data)==0:
            raise Exception("API empty")

        return pd.DataFrame(data)

    except:

        # fallback data if API fails
        demo_data=[
            {"Crypto":"Bitcoin","Price":60000},
            {"Crypto":"Ethereum","Price":3000},
            {"Crypto":"Binancecoin","Price":500},
            {"Crypto":"Cardano","Price":0.5},
            {"Crypto":"Solana","Price":150},
        ]

        return pd.DataFrame(demo_data)

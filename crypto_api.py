import requests, pandas as pd

def fetch_data():
    ids="bitcoin,ethereum,binancecoin,cardano,solana"
    url=f"https://api.coingecko.com/api/v3/simple/price?vs_currencies=usd&ids={ids}"
    res=requests.get(url).json()

    data=[]
    for c in res:
        data.append({"Crypto":c.capitalize(),"Price":res[c]["usd"]})

    return pd.DataFrame(data)

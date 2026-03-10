import requests
import pandas as pd

API_KEY="CG-HdRxpnS5T616DTh22gcRGyRG"

def fetch_crypto_prices():

    ids="bitcoin,ethereum,binancecoin,cardano,solana"

    url=f"https://api.coingecko.com/api/v3/simple/price?vs_currencies=usd&ids={ids}&x_cg_demo_api_key={API_KEY}"

    res=requests.get(url).json()

    data=[]
    for coin in res:
        data.append({
            "Crypto":coin.capitalize(),
            "Price":res[coin]["usd"]
        })

    return pd.DataFrame(data)

import pandas as pd
from concurrent.futures import ThreadPoolExecutor

def calc_risk(data):
    vol=data["Close"].std()
    if vol>2000: return "High"
    elif vol>1000: return "Medium"
    return "Low"

def run_risk_checks(df):
    groups=[g for _,g in df.groupby("Crypto")]
    with ThreadPoolExecutor() as ex:
        risks=list(ex.map(calc_risk,groups))
    return pd.DataFrame({"Crypto":df["Crypto"].unique(),"Risk":risks})

import pandas as pd
from concurrent.futures import ThreadPoolExecutor

def calc_risk(row):
    if row["Price"]>30000: return "High"
    elif row["Price"]>10000: return "Medium"
    return "Low"

def run_risk_checks(df):

    with ThreadPoolExecutor() as ex:
        risks=list(ex.map(calc_risk,[row for _,row in df.iterrows()]))

    return pd.DataFrame({
        "Crypto":df["Crypto"],
        "Risk":risks
    })

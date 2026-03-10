# =====================================================
# RISK CHECKER (PARALLEL)
# =====================================================

import pandas as pd
from concurrent.futures import ThreadPoolExecutor


# ---------------- SINGLE RISK CHECK ----------------
def calc_risk(row):

    # simple rule-based risk logic
    if row["Price"] > 30000:
        return "High"

    elif row["Price"] > 10000:
        return "Medium"

    else:
        return "Low"


# ---------------- PARALLEL RISK CHECK ----------------
def run_risk(df):

    # convert rows to list
    rows=[row for _,row in df.iterrows()]

    with ThreadPoolExecutor() as executor:
        risks=list(executor.map(calc_risk,rows))

    result=pd.DataFrame({
        "Crypto":df["Crypto"],
        "Price":df["Price"],
        "Risk":risks
    })

    return result

import pandas as pd

def calculate_mix(df,amount,risk):

    df["Return"]=df.Price/df.Price.max()
    df["Vol"]=df.Price/df.Price.mean()

    df["Return_n"]=df.Return/df.Return.max()
    df["Vol_n"]=df.Vol/df.Vol.max()

    if risk=="Low":
        df["Score"]=.7*(1-df.Vol_n)+.3*df.Return_n
    elif risk=="Medium":
        df["Score"]=.5*(1-df.Vol_n)+.5*df.Return_n
    else:
        df["Score"]=.3*(1-df.Vol_n)+.7*df.Return_n

    df["Allocation %"]=df.Score/df.Score.sum()*100
    df["Investment"]=df["Allocation %"]/100*amount

    return df

import pandas as pd



def convert_transactions(df):
    df = df.copy()
    df["shares"] = pd.to_numeric(df["shares"], errors='coerce')
    df["price"] = pd.to_numeric(df["price"], errors='coerce')
    return df

def add_value(df):
    df = df.copy()
    check = df["code"].isin(["P", "S"])
    df.loc[check, "value"] = df.loc[check, "shares"] * df.loc[check, "price"]
    df["value"] = df["value"].round(2)
    return df

def get_top_purchases(df):
    purchases = df[df["code"] == "P"]
    purchases = purchases.sort_values("value", ascending=False)
    return purchases
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

def get_top_activity(df):
    activity = df[df["code"].isin(["P", "S"])]
    activity = activity.sort_values("value", ascending=False)
    return activity

def format_value(value):
    if value >= 1_000_000_000:
        return f"${value/1_000_000_000:.1f}B"
    elif value >= 1_000_000:
        return f"${value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"${value/1_000:.1f}K"
    else:
        return f"${value:,.0f}"

def format_name(name):
    order = name.split()
    if len(order) < 2:
        return name
    if len(order) == 3:
        return " ".join([order[1], order[2], order[0]])
    return " ".join([order[1], order[0]])


def format_date(date):
    if pd.isnull(date):
        return "Unknown"
    return date.strftime("%m/%d/%Y")

def cluster_buying(df):
    purchases = df[df["code"] == "P"]
    unique_buyers = purchases.groupby("ticker")["name"].nunique()
    clusters = unique_buyers[unique_buyers >= 3]

    tickers = clusters.index.tolist()
    detects = df[(df["code"] == "P") & (df["ticker"].isin(tickers))]

    return detects.sort_values(["ticker", "date"])



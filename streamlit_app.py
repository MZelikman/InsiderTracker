import streamlit as st
import pandas as pd
from database import get_connection
from datetime import datetime, timedelta
from process_data import get_top_purchases, get_top_activity, format_value, format_name, format_date
from price_history import get_current_price, get_price_change
st.set_page_config(layout="wide")

st.title("Insider Trading Tracker")

conn = get_connection()
df = pd.read_sql("SELECT * FROM transactions", conn)
conn.close()

df["date"] = pd.to_datetime(df["date"])

top_cutoff = pd.Timestamp.now() - pd.Timedelta(days=60)
top_df = df[df["date"] >= top_cutoff]

top_activity = get_top_activity(top_df).head(5)

st.subheader("TOP INSIDER ACTIVITY")

cols = st.columns(len(top_activity))
one_month_ago = (datetime.now() - timedelta(days=90))
count = 0

for i, row in enumerate(top_activity.itertuples()):
        with cols[i]:
            card = st.container(border=True, height="stretch", width="stretch")
            with card:
                st.caption(f"{row.ticker} · {format_date(row.date)}")
                st.write(f"**{format_name(row.name)}**")
                label = "BUY" if row.code == "P" else "SELL"
                st.metric(
                    label= label,
                    value=format_value(row.value),
                    delta=f"{row.shares:,.0f} shares",
                    delta_color="normal" if row.code == "P" else "inverse"
                )


                


st.subheader("Search Stocks")
MAG7 = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"]
selected_ticker = st.selectbox("Company (Mag 7 for now):", ["All"] + MAG7, index=0)

days_back = st.selectbox("Show activity from the last:", [30, 60, 90, 270], index=3)
st.subheader("Insider Signals")

left_col, right_col = st.columns(2)

today = datetime.now().date()
cutoff = pd.Timestamp.now() - pd.Timedelta(days=days_back)
filtered_df = df[df["date"] >= cutoff]

if selected_ticker != "All":
    filtered_df = filtered_df[filtered_df["ticker"] == selected_ticker]

top_three = get_top_purchases(filtered_df).head(3)

with left_col:
    price_card = st.container(border=True, height="stretch")
    with price_card:
        st.write("**Price Since Filing**")
        st.write("Biggest 3 Purchases")

        if selected_ticker == "All":
            st.caption("Select a specific ticker to see price comparison")
        elif top_three.empty:
            st.caption("No purchases found in this window")
        else:
            current_price = get_current_price(selected_ticker)

            if current_price is None:
                st.caption("Price data unavailable right now")
            else:
                for row in top_three.itertuples():
                    change = get_price_change(row.price, current_price)
                    if change is None:
                        continue

                    entry = st.container(border=True)
                    with entry:
                        st.caption(f"{format_name(row.name)} · bought at ${row.price:.2f}")
                        st.metric(
                            label=f"Since {format_date(row.date)}",
                            value=f"${current_price:.2f}",
                            delta=f"{change:+.1f}%",
                            delta_color="normal" if change >= 0 else "inverse"
                        )
                  

with right_col:
    ratio_card = st.container(border=True, height="stretch")
    with ratio_card:
        st.write("**Buy / Sell Ratio**")

        buys = len(filtered_df[filtered_df["code"] == "P"])
        sells = len(filtered_df[filtered_df["code"] == "S"])
        total = buys + sells


        if selected_ticker == "All":
            st.caption("Select a specific ticker to see price comparison")
        elif total == 0:
            st.caption("No buy/sell activity in this window")
        else:
            buy_pct = buys / total * 100
            sentiment = "Bullish" if buy_pct > 60 else "Bearish" if buy_pct < 40 else "Mixed"
            sentiment_color = "normal" if buy_pct >= 50 else "inverse"

            st.metric(
                label="Insider Sentiment",
                value=sentiment,
                delta=f"{buy_pct:.0f}% buys / {sell_pct:.0f}% sells" if False else f"{buys} buys, {sells} sells",
                delta_color=sentiment_color
            )
            st.progress(buy_pct / 100)




st.subheader(f"Cluster Buying · {selected_ticker}")
st.write("Purchases from 3+ different insiders")


st.subheader("All Data")
with st.expander("See all transactions"):
    st.dataframe(df)

import streamlit as st
import pandas as pd
from database import get_connection
from datetime import datetime, timedelta
from process_data import get_top_purchases, get_top_activity, format_value, format_name, format_date, cluster_buying
from price_history import get_current_price, get_price_change
 
st.set_page_config(
    page_title="Insider Trading Tracker",
    page_icon="📈",
    layout="wide",
)
 

st.markdown("""
<style>
    .block-container { padding-top: 2.5rem; }
     h2, h3 { letter-spacing: 0.3px; }
     [data-testid="stMetricValue"] { font-size: 1.6rem; }
</style>
""", unsafe_allow_html=True)
 

conn = get_connection()
df = pd.read_sql("SELECT * FROM transactions", conn)
conn.close()
 
df["date"] = pd.to_datetime(df["date"])
 

st.sidebar.title("Filters")
 
MAG7 = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"]
selected_ticker = st.sidebar.selectbox("Company", ["All"] + MAG7, index=0)
st.sidebar.caption("Search coming soon — Mag 7 for now")
 
days_back = st.sidebar.selectbox(
    "Show activity from the last (days)",
    [30, 60, 90, 270],
    index=3,
)

cutoff = pd.Timestamp.now() - pd.Timedelta(days=days_back)
filtered_df = df[df["date"] >= cutoff]
if selected_ticker != "All":
    filtered_df = filtered_df[filtered_df["ticker"] == selected_ticker]
 

st.title("Insider Trading Tracker")
st.caption(
    "Corporate insider stock activity pulled directly from SEC EDGAR filings. "
    "Surfacing patterns in insider buying to help judge whether it signals anything."
)
 
st.divider()
 

st.subheader("Top Insider Activity")
 
top_cutoff = pd.Timestamp.now() - pd.Timedelta(days=60)
top_df = df[df["date"] >= top_cutoff]
top_activity = get_top_activity(top_df).head(4)
 
if top_activity.empty:
    st.info("No insider activity found in the last 60 days.")
else:
    cols = st.columns(len(top_activity))
    for i, row in enumerate(top_activity.itertuples()):
        with cols[i]:
            card = st.container(border=True, height="stretch")
            with card:
                st.caption(f"{row.ticker}  ·  {format_date(row.date)}")
                st.write(f"**{format_name(row.name)}**")
                is_buy = row.code == "P"
                label = "BUY" if is_buy else "SELL"

                share_delta = row.shares if is_buy else -row.shares
                st.metric(
                    label=label,
                    value=format_value(row.value),
                    delta=f"{share_delta:,.0f} shares",
                    delta_color="normal",
                )
 
st.divider()
 

st.subheader("Insider Signals")
if selected_ticker == "All":
    st.caption("Showing all companies · pick one in the sidebar for price detail")
else:
    st.caption(f"Showing {selected_ticker} · last {days_back} days")
 
left_col, right_col = st.columns(2)
 
top_three = get_top_purchases(filtered_df).head(3)
 
with left_col:
    price_card = st.container(border=True, height="stretch")
    with price_card:
        st.markdown("**Price Since Filing**")
        st.caption("Biggest 3 purchases, compared to the current price")
 
        if selected_ticker == "All":
            st.info("Select a company in the sidebar to compare prices.")
        elif top_three.empty:
            st.info("No purchases found in this window.")
        else:
            current_price = get_current_price(selected_ticker)
            if current_price is None:
                st.warning("Price data unavailable right now.")
            else:
                for row in top_three.itertuples():
                    change = get_price_change(row.price, current_price)
                    if change is None:
                        continue
                    entry = st.container(border=True)
                    with entry:
                        st.caption(f"{format_name(row.name)} · bought at ${row.price:.2f}")
                        st.metric(
                            label=f"Now (since {format_date(row.date)})",
                            value=f"${current_price:.2f}",
                            delta=f"{change:+.1f}%",
                            delta_color="normal" if change >= 0 else "inverse",
                        )
 

with right_col:
    ratio_card = st.container(border=True, height="stretch")
    with ratio_card:
        st.markdown("**Buy / Sell Ratio**")
        st.caption("Insider sentiment across the selected window")
 
        buys = len(filtered_df[filtered_df["code"] == "P"])
        sells = len(filtered_df[filtered_df["code"] == "S"])
        total = buys + sells
 
        if total == 0:
            st.info("No buy/sell activity in this window.")
        else:
            buy_pct = buys / total * 100
            sell_pct = sells / total * 100
            sentiment = "Bullish" if buy_pct > 60 else "Bearish" if buy_pct < 40 else "Mixed"
            sentiment_color = "normal" if buy_pct >= 50 else "inverse"
 
            st.metric(
                label="Insider Sentiment",
                value=sentiment,
                delta=f"{buys} buys · {sells} sells",
                delta_color=sentiment_color,
            )
            st.progress(buy_pct / 100)
            st.caption(f"{buy_pct:.0f}% buys · {sell_pct:.0f}% sells")
 
st.divider()
 

st.subheader("Cluster Buying")
st.caption(
    f"Companies where 3+ different insiders bought · "
    f"{selected_ticker if selected_ticker != 'All' else 'all companies'}"
)

cluster_information = cluster_buying(filtered_df)

cluster_card = st.container(border=True)
with cluster_card:
    if cluster_information.empty:
        st.info("No cluster buying detected in this window.")
    else:
        for ticker, group in cluster_information.groupby("ticker"):
            n_insiders = group["name"].nunique()
            total_value = group["value"].sum()
            st.write(f"**{ticker}** — {n_insiders} distinct insiders · {format_value(total_value)} total")
            for row in group.itertuples():
                st.caption(f"{format_name(row.name)} bought {format_value(row.value)} on {format_date(row.date)}")
            st.divider()
 
st.divider()
 

st.subheader("All Transactions")
with st.expander("View the full filtered dataset"):
    st.dataframe(filtered_df, width="stretch")

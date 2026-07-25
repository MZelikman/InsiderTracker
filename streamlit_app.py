import streamlit as st
import pandas as pd
from database import get_connection
from process_data import get_top_purchases, get_top_activity, format_value, format_name, format_date
st.set_page_config(layout="wide")

st.title("Insider Trading Tracker")




conn = get_connection()
df = pd.read_sql("SELECT * FROM transactions", conn)
conn.close()


top_activity = get_top_activity(df).head(5)

st.subheader("TOP INSIDER ACTIVITY")

cols = st.columns(len(top_activity))

for i, row in enumerate(top_activity.itertuples()):
    with cols[i]:
        card = st.container(border=True, height="stretch", width="stretch")
        with card:
            st.caption(f"{row.ticker} · {format_date(row.date)}")
            st.write(f"**{format_name(row.name)}**")
            label = "BUY" if row.code == "P" else "SELL"
            st.metric(
                label= f"label {row.date}",
                value=format_value(row.value),
                delta=f"{row.shares:,.0f} shares",
                delta_color="normal" if row.code == "P" else "inverse"
            )


with st.expander("See all transactions"):
    st.dataframe(df)
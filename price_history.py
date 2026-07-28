import yfinance as yf

def get_current_price(ticker):
    stock = yf.Ticker(ticker)
    history = stock.history(period="1d")
    if history.empty:
        return None
    return history["Close"].iloc[-1]


def get_price_change(current, before):
    if current is None or before == 0:
        return None
    return (current - before) / before * 100


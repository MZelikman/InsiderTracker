import pandas as pd
import time
from fetch_data import get_insider_transactions, get_ticker_to_cik, get_filings_ticker, POPULAR_TICKERS
from process_data import convert_transactions, add_value, get_top_purchases
from database import get_connection, save_transactions
from datetime import datetime, timedelta


ticker_to_cik = get_ticker_to_cik();
transaction_log = []
six_months_ago = (datetime.now() - timedelta(days=270)).strftime("%Y-%m-%d")

for tk in POPULAR_TICKERS:
    filings, cik = get_filings_ticker(tk, ticker_to_cik)

    forms = filings["filings"]["recent"]["form"]
    dates = filings["filings"]["recent"]["filingDate"]
    accession_numbers = filings["filings"]["recent"]["accessionNumber"]

    
    for i in range(len(forms)):
        if forms[i] == "4" and dates[i] >= six_months_ago:
            try:
                insiders = get_insider_transactions(cik, accession_numbers[i])
                for t in insiders:
                    t["ticker"] = tk 
                transaction_log.extend(insiders)
            except Exception as e:
                print(f"Skipped: {tk} {accession_numbers[i]} : {e}")

            time.sleep(0.2)


df = pd.DataFrame(transaction_log)



df = convert_transactions(df)
df = add_value(df)


save_transactions(df)
print("Saved")

top_purchases = get_top_purchases(df)
print("Top Purchases:")
print(top_purchases.head(10))

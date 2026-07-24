import pandas as pd
import time
from fetch_data import get_insider_transactions, get_ticker_to_cik, get_filings_ticker, POPULAR_TICKERS


ticker_to_cik = get_ticker_to_cik();
transaction_log = []

for tk in POPULAR_TICKERS:
    filings, cik = get_filings_ticker(tk, ticker_to_cik)

    forms = filings["filings"]["recent"]["form"]
    dates = filings["filings"]["recent"]["filingDate"]
    accession_numbers = filings["filings"]["recent"]["accessionNumber"]

    
    count = 0
    for i in range(len(forms)):
        if forms[i] == "4":
            if (count > 5):
                break
            count += 1
            try:
                insiders = get_insider_transactions(cik, accession_numbers[i])
                for t in insiders:
                    t["ticker"] = tk 
                transaction_log.extend(insiders)
            except Exception as e:
                print(f"Skipped: {tk} {accession_numbers[i]} : {e}")

            time.sleep(0.2)


df = pd.DataFrame(transaction_log)
print(df)

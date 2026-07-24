import requests
import xml.etree.ElementTree as ET

headers = {"User-Agent": "Maxim Zelikman zelikmanmaxim@gmail.com"}

POPULAR_TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "MU"]


def get_ticker_to_cik():
    tickers_url = "https://www.sec.gov/files/company_tickers.json"
    tickers_response = requests.get(tickers_url, headers=headers)
    tickers_data = tickers_response.json()
    ticker_to_cik = {v["ticker"]: str(v["cik_str"]).zfill(10) for v in tickers_data.values()}
    return ticker_to_cik

def get_filings(cik):
    filings_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    filings_response = requests.get(filings_url, headers=headers)
    filings = filings_response.json()
    return filings

def get_filings_ticker(ticker, ticker_to_cik):
    cik = ticker_to_cik[ticker]
    filings = get_filings(cik)
    return filings, cik

def get_insider_transactions(cik, accession):

    accession_no_dashes = accession.replace("-", "")
    xml_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_no_dashes}/form4.xml"
    xml_response = requests.get(xml_url, headers=headers)
    root = ET.fromstring(xml_response.text)

    name = root.find(".//rptOwnerName")

    transactions = root.findall(".//nonDerivativeTransaction")

    trades = []
    for t in transactions:
        code = t.find(".//transactionCode")
        shares = t.find(".//transactionShares/value")
        price = t.find(".//transactionPricePerShare/value")

        trades.append({
            "name": name.text if name is not None else None,
            "code": code.text if code is not None else None,
            "shares": shares.text if shares is not None else None,
            "price": price.text if price is not None else None,
        })

    return trades

    







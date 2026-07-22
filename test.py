import requests
import xml.etree.ElementTree as ET
import pandas as pd

headers = {"User-Agent": "Maxim Zelikman zelikmanmaxim@gmail.com"}

url = "https://www.sec.gov/files/company_tickers.json"
response = requests.get(url, headers=headers)

data = response.json()

ticker_to_cik = {v["ticker"]: str(v["cik_str"]).zfill(10) for v in data.values()}

cik = ticker_to_cik["AAPL"]
url2 = f"https://data.sec.gov/submissions/CIK{cik}.json"
response2 = requests.get(url2, headers=headers)
filings = response2.json()

forms = filings["filings"]["recent"]["form"]
dates = filings["filings"]["recent"]["filingDate"]
accession_numbers = filings["filings"]["recent"]["accessionNumber"]


accession = "0001140361-26-025622"
accession_no_dashes = accession.replace("-", "")


index_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_no_dashes}/{accession}-index.htm"


xml_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_no_dashes}/form4.xml"
response3 = requests.get(xml_url, headers=headers)


root = ET.fromstring(response3.text)


name = root.find(".//rptOwnerName")


transactions = root.findall(".//nonDerivativeTransaction")

all_transactions = []

for t in transactions:
    code = t.find(".//transactionCode")
    shares = t.find(".//transactionShares/value")
    price = t.find(".//transactionPricePerShare/value")

    transaction_data = {
            "name": name.text,
            "code": code.text if code is not None else "N/A",
            "shares": shares.text if shares is not None else "N/A",
            "price": price.text if price is not None else "N/A"
    }

    all_transactions.append(transaction_data)

df = pd.DataFrame(all_transactions)

purchases = df[df["code"] == "M"]
print(purchases)









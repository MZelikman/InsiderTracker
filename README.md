# Insider Trading Tracker

## Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [Technologies Used](#technologies-used)
- [Installation & Setup](#installation--setup)
- [Project Structure](#project-structure)
- [Data Pipeline](#data-pipeline)
- [Example Workflow](#example-workflow)
- [What I Learned](#what-i-learned)
- [Overall Impact](#overall-impact)
- [Contact](#contact)

## Overview

This project automates the collection, processing, storage, and visualization of corporate insider stock transaction data, sourced directly from the SEC's EDGAR system, for a curated set of major public companies. It integrates data engineering, custom financial analytics, and an interactive dashboard to build a reproducible pipeline that:

- Eliminates manual filing lookups by automating direct retrieval from SEC EDGAR's public API
- Parses raw Form 4 XML filings into structured, human-readable transaction records
- Classifies transactions by type (open-market purchase, sale, option exercise, award, tax withholding) to isolate genuinely meaningful insider activity from routine compensation events
- Calculates transaction dollar value and ranks the largest recent insider buys and sells
- Detects cluster buying, where multiple distinct insiders purchase the same company within a given window
- Compares an insider's purchase price to the current market price using live data
- Persists processed data locally, so the dashboard loads instantly without re-querying SEC on every view
- Surfaces all of the above through an interactive Streamlit dashboard, so the underlying question can be explored: does insider buying activity carry a meaningful signal?

## Key Features

- **End-to-End Data Pipeline** — From raw SEC EDGAR API calls to structured, analysis-ready datasets
- **Multi-Company Tracking** — Monitors a curated list of major tickers, with a scalable structure for expanding coverage
- **Direct XML Filing Parsing** — Extracts reporting owner, transaction code, share count, price, and date straight from raw Form 4 filings, with no third-party financial data provider required
- **Transaction Classification** — Distinguishes genuine open-market buys/sells from option exercises, stock awards, and tax-related transactions
- **Cluster Buying Detection** — Flags companies where three or more distinct insiders bought within the selected window, a stronger signal than any single purchase
- **Price Since Filing** — Integrates live market data to show how a stock has moved since an insider's largest recent purchases
- **Buy/Sell Sentiment** — Summarizes insider sentiment per company as a buy/sell ratio with a bullish/bearish/mixed read
- **Rolling Date Filtering** — Interactive control to adjust how far back the dashboard looks
- **Persistent Local Storage** — SQLite-backed caching so the dashboard doesn't depend on live API calls to render
- **Interactive Dashboard** — Card-based feed of top insider activity, sidebar filters, and per-company signal breakdowns, built with Streamlit

## Technologies Used

**Languages & Core Libraries**
- Python 3
- `xml.etree.ElementTree`, `datetime`, `time`

**API Integration**
- `requests` — HTTP calls to the SEC EDGAR API (ticker lookup, filing submissions, raw XML filings)
- `yfinance` — live/current market price lookups for price-since-filing comparison

**Data Analysis & Processing**
- `pandas` — data cleaning, type conversion, grouping, and transaction-level analytics

**Storage**
- `sqlite3` — lightweight local persistence layer

**Dashboard**
- `streamlit` — interactive frontend, custom dark theme via `.streamlit/config.toml`

## Installation & Setup

**1. Clone Repository**
```
git clone https://github.com/yourusername/insider-trading-tracker.git
cd insider-trading-tracker
```

**2. (Optional But Recommended) Create a Virtual Environment**

Create and activate a virtual environment to isolate dependencies.
```
# Create the virtual environment
python -m venv venv

# Activate the environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

**3. Install Requirements**
```
pip install -r requirements.txt
```

**4. Configure SEC API Access**

No API key is required — SEC EDGAR is a free, public, unauthenticated API. The only requirement is a valid `User-Agent` header identifying the requester (name and email), set in `fetch_data.py`.

**5. Update Configuration**

`fetch_data.py` contains the `POPULAR_TICKERS` list, which defines which companies the pipeline tracks. Add or remove tickers as needed.

## Project Structure

```
fetch_data.py          # SEC EDGAR API calls, ticker/CIK lookup, Form 4 XML parsing
process_data.py         # Cleaning, value calculation, transaction classification,
                         # name/date formatting, top-activity ranking, cluster detection
price_history.py        # Live current-price lookups and price-change calculation (yfinance)
database.py              # SQLite connection, save/read functions
main.py                  # Orchestrates the pipeline: fetch -> process -> store
app.py                    # Streamlit dashboard, reads from the local database

.streamlit/
  config.toml            # Dashboard theme configuration

data/
  insiders.db             # SQLite database (generated locally)

.gitignore                # Lists files/folders Git should ignore
requirements.txt          # Python packages and versions needed to run the project
```

## Data Pipeline

**1. Ticker & CIK Resolution — `fetch_data.py`**

Automates retrieval of SEC's full ticker-to-CIK mapping in a single call, cached for reuse across the entire pipeline run.
- Zero-padded CIK formatting to match EDGAR's required format
- Single lookup shared across every ticker, avoiding redundant network calls

**2. Filing History Retrieval — `fetch_data.py`**

Pulls each tracked company's filing submission history from SEC's submissions endpoint.
- Returns parallel, position-aligned arrays (form type, filing date, accession number) which the pipeline aligns by index
- Filtered to Form 4 filings within a rolling recent window rather than full historical depth

**3. Raw XML Filing Parsing — `fetch_data.py`**

For each relevant Form 4 filing, fetches and parses the underlying XML document to extract:
- Reporting owner name
- Transaction code (buy, sell, option exercise, award, tax withholding, etc.)
- Share count and price per share
- Transaction date

Defensive `None` handling ensures a missing field in an individual filing doesn't break the pipeline.

**4. Data Cleaning & Feature Calculation — `process_data.py`**

- Converts raw text fields (shares, price) to numeric types
- Calculates total transaction dollar value (shares × price), applied only to genuine market transactions (buy/sell codes)
- Reformats reporting owner names from SEC's `Last First Middle` filing format into a standard `First Middle Last` display format
- Formats large dollar values and dates for clean display

**5. Analysis & Ranking — `process_data.py`**

- Filters to open-market purchases, or purchases and sales combined, depending on the view
- Ranks transactions by dollar value to surface the most significant recent insider activity
- Detects cluster buying by grouping purchases per company and counting distinct insiders, flagging companies that meet a minimum-insider threshold

**6. Live Price Comparison — `price_history.py`**

Fetches the current market price for a selected ticker and computes the percentage change relative to an insider's purchase price, giving a "how has this played out since the filing" view.

**7. Persistent Storage — `database.py`**

Writes the fully processed dataset to a local SQLite database, replacing prior data on each run. This decouples the dashboard from SEC's API entirely — the dashboard only ever reads from local storage, so it loads instantly regardless of how long the underlying fetch took.

**8. Dashboard — `app.py`**

Reads directly from the SQLite database and renders:
- A card-based feed of the largest recent insider purchases and sales, color- and direction-coded by transaction type
- Sidebar filters for company and lookback window that drive every section below them
- A price-since-filing panel and a buy/sell sentiment panel
- A cluster-buying section highlighting coordinated insider activity
- A full, filterable transaction table for deeper inspection
- A custom dark theme matching a financial-dashboard aesthetic

## Example Workflow

```
# 1. Fetch, process, and store the latest insider filings
python main.py

# 2. Launch the interactive dashboard
streamlit run app.py
```

## What I Learned

Key takeaways include:

**API Integration & Raw Data Parsing**
- Learned to work directly with a government API (SEC EDGAR) 
- Gained experience parsing raw XML filings 

**Domain-Specific Data Modeling**
- Learned the practical meaning behind SEC Form 4 transaction codes, producing a meaningful signal rather than noisy data
- Designed cluster-buying detection around distinct insiders rather than raw transaction counts

**Data Pipeline Architecture**
- Structured the project into distinct fetch, process, storage, and presentation layers
- Learned why persistent local storage matters even for a personal project

**Performance & Reliability Considerations**
- Learned to balance data freshness against runtime
- Added defensive error handling so a single malformed or unusual filing doesn't halt the entire pipeline

**Dashboard Design**
- Applied UI/UX principles 

## Overall Impact

This project strengthened my ability to connect real-world API integration and data pipeline design into a single working system. I gained hands-on experience parsing unfamiliar data, translating raw filings into a meaningful analytical signal, and presenting that signal through a clean, interactive interface. This project helped my understanding of working through a codebase and my ability to take a project from a research question to a product independently.

## Visuals

<img width="2560" height="1184" alt="image" src="https://github.com/user-attachments/assets/2c12d2fc-c17d-4191-8b37-86c23206d850" />
<img width="2560" height="1174" alt="image" src="https://github.com/user-attachments/assets/d4de2053-db39-4151-bf18-9ab0344bb99c" />



## Contact

For questions or feedback, feel free to reach out:

- **Email:** zelikmanmaxim@gmail.com

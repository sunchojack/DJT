# GDELT vs DJT-coin: who would win?

This project analyzes the relationship between GDELT (Global Database of Events, Language, and Tone) data on "Trump" mentions and DJT (Trump Media & Technology) stock prices.
Assumption: more positive media coverage of Trump leads to better stock performance of his DJT company.

The main idea was, however, to have a pipeline for GDELT and for stock data (Yahoo).

## Scripts Overview

#### `GET_yahoo_stockdata.py`
**Purpose**: Fetches historical stock data for DJT (Trump Media & Technology) from **Yahoo Finance**.

**What it does**:
- Downloads daily stock data for a defined period of time
- Saves data to `workdata/stock.csv`
- CAN BE USED TO FETCH *MULTIPLE* STOCK TICKERS by modifying the ticker symbol and company in the list

**Works**: Yes, successfully fetches and saves stock data. User has to set up the ticker selection manually in the script.

#### `GDELT_docapi.py`
**Purpose**: Fetches GDELT article data using the [gdeltdoc](https://github.com/alex9smith/gdelt-doc-api) library by alex9smith.
Since it is a github user library, deemed to be unstable; was hitting rate limits.

**What it does**:
- Searches GDELT for articles mentioning a keyword in a region (set in f = ...)
- Processes data daily within a defined timeframe
- Saves each day's results to daily CSV files in `gdelt_doc_api_daily/` folder
- REQUIRES FURTHER PROCESSING to combine daily files into a single dataset (not implemented)

**Works**: May hit API rate limits depending on the time and usage. One month works fine.

#### `GDELT_proper.py`
**Purpose**: Fetches GDELT article data using from GDELT's own API. The downside is that it first
has to fetch the full GDELT dataset and THEN filter based on the keywords. Still used,
since it's more stable.

**What it does**:
- Searches GDELT for articles during a specified timeframe
- Filters by keyword specified inside the script
- Saves the full filtered results to `gdelt_results.csv`

**Works**: Much slower but more reliable than `GDELT_docapi.py`. Does not require further processing, 
although filtering and keeping the large dataset in active memory is a problem.

#### `get_processed_GDELTtones.py`

**Purpose**: The final script that used GDELT's V2Tone data (news sentiment) and the stock figures to 
create naive regressions and plots. Discontinued due to the need for a more comprehensive analysis; the
idea of the project. Can be reused by adding support scripts that would:
- process V2Tone data in a more thoughtful way
- match news and stock data based on timestamps + timezones, as well as to account for time lags (next trading day etc.)

## Dependencies
- pandas
- yfinance
- gdelt
- gdeltdoc
- dask
- matplotlib
- scipy
- seaborn

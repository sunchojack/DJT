import pandas as pd
import yfinance as yf

# List of companies and their tickers
companies = [
    {"name": "Trump Media & Technology", "ticker": "DJT"},
    ]

# Function to fetch historical market cap data
def fetch_yahoo(ticker):
    data = yf.download(ticker, start="2024-01-01", end="2024-06-25", interval='1d')
    # return data[['Adj Close']]
    return data

# Fetch the data for each company and store it in a dictionary
data_out = {}
for company in companies:
    print(f"Fetching data for {company['name']} ({company['ticker']})")
    try:
        data_out[company['name']] = fetch_yahoo(company['ticker'])
    except Exception as e:
        print(f"Failed to fetch data for {company['name']} ({company['ticker']}): {e}")

# Combine all the data into a single DataFrame
combined_df = pd.concat(data_out, axis=1)

# Save to CSV
file_path = "workdata/stock.csv"
combined_df.to_csv(file_path)

print(f"Data saved to {file_path}")
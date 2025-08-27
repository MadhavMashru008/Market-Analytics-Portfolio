import pandas as pd
import yfinance as yf
from datetime import datetime

# Define tickers and date range
tickers = ['GS', 'MSFT', 'JPM', 'AAPL', 'V']
start_date = '2023-01-01'
end_date = datetime.now().strftime('%Y-%m-%d')

print("Fetching historical stock data...")

# Download data and concatenate into a single DataFrame
all_data = pd.DataFrame()
for ticker in tickers:
    try:
        data = yf.download(ticker, start=start_date, end=end_date)
        if not data.empty:
            data['Ticker'] = ticker
            all_data = pd.concat([all_data, data])
    except Exception as e:
        print(f"Could not download data for {ticker}: {e}")

# Reset the index to create a 'Date' column from the index
all_data.reset_index(inplace=True)

# Save the raw data to a CSV file
output_path = 'raw_stock_data.csv'
all_data.to_csv(output_path, index=False)
print(f"Data saved to {output_path}")
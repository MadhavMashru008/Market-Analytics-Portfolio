import pandas as pd
from alpha_vantage.timeseries import TimeSeries
import numpy as np
import warnings

warnings.filterwarnings('ignore')

def run_project():
    """
    Main function to run the entire data analytics workflow with a live API.
    """
    # Replace with your actual Alpha Vantage API Key
    api_key = 'UU6IA6Z902YFSC68'

    tickers = ['GS', 'MSFT', 'JPM', 'AAPL', 'V']
    
    print("Fetching intraday stock data from Alpha Vantage API...")

    ts = TimeSeries(key=api_key, output_format='pandas')
    all_data = pd.DataFrame()

    for ticker in tickers:
        try:
            # Get intraday data, which is a free endpoint
            data, meta_data = ts.get_intraday(symbol=ticker, interval='5min', outputsize='full')
            
            # Ensure the required columns are present
            if not data.empty and '4. close' in data.columns and '5. volume' in data.columns:
                # Rename columns for consistency and clean up the data
                data.rename(columns={'4. close': 'Adj Close', '5. volume': 'Volume'}, inplace=True)
                data['Ticker'] = ticker
                
                all_data = pd.concat([all_data, data])
            else:
                print(f"Skipping {ticker}: Required columns not found or data is empty.")
        except Exception as e:
            print(f"Could not download data for {ticker}: {e}")

    if all_data.empty:
        print("\nError: No data was downloaded successfully. Please check your internet connection or API key. Exiting.")
        return

    # Step 2: Analysis and Feature Engineering
    print("\nPerforming analysis and feature engineering...")
    
    df = all_data.copy()
    df.index = pd.to_datetime(df.index)
    df.dropna(inplace=True)

    # Calculate daily returns and rolling volatility
    df['Daily Return'] = df.groupby('Ticker')['Adj Close'].pct_change()
    df['Rolling Volatility'] = df.groupby('Ticker')['Daily Return'].transform(lambda x: x.rolling(window=20).std())

    # Calculate Volume Change
    df['Volume Change'] = df.groupby('Ticker')['Volume'].pct_change()
    
    # Reset index for Power BI compatibility
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'Date'}, inplace=True)
    
    # Step 3: Final Output to Excel
    output_path = 'financial_data_ready_for_powerbi.xlsx'
    df.to_excel(output_path, index=False)
    print(f"\nProcessed data saved to {output_path}. You can now use this file in Power BI.")

if __name__ == '__main__':
    run_project()
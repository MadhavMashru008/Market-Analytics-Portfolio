import pandas as pd
from statsmodels.tsa.api import ExponentialSmoothing
import numpy as np

# Load the raw data, explicitly naming the columns we need
try:
    df = pd.read_csv('raw_stock_data.csv', usecols=['Date', 'Adj Close', 'Ticker'])
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
except FileNotFoundError:
    print("Error: 'raw_stock_data.csv' not found. Please run data_ingestion.py first.")
    exit()

# Clean and prepare the data
df.dropna(inplace=True)
df['Daily Return'] = df.groupby('Ticker')['Adj Close'].pct_change()
df['Rolling Volatility'] = df.groupby('Ticker')['Daily Return'].transform(lambda x: x.rolling(window=20).std())

# Simple forecasting using Exponential Smoothing for one ticker (for MVP)
# We will forecast Goldman Sachs (GS) as an example
gs_data = df[df['Ticker'] == 'GS']['Adj Close'].asfreq('B').ffill()
fit = ExponentialSmoothing(gs_data, seasonal_periods=5, trend='add', seasonal='add').fit()
forecast = fit.forecast(steps=5)

# Append forecast to the dataframe (simple way for Power BI)
forecast_df = pd.DataFrame(forecast, columns=['Forecasted Price'])
forecast_df['Ticker'] = 'GS'
df.reset_index(inplace=True)
df = pd.concat([df, forecast_df], ignore_index=True)


# Save the final, processed data for Power BI
output_path = 'processed_market_data.xlsx'
df.to_excel(output_path, index=False)
print(f"Processed data with analytics and forecasts saved to {output_path}")
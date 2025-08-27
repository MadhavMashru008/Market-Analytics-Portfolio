import streamlit as st
import pandas as pd
import yfinance as yf
from math import sqrt
from datetime import datetime, timedelta

st.set_page_config(page_title="Market Analytics", layout="wide")

TICKERS = ["AAPL","GS","JPM","MSFT","V"]
PERIOD = "6mo"
INTERVAL = "1d"
ROLL_WINDOW = 20

@st.cache_data(ttl=3600)
def load_prices(tickers, period, interval):
    data = yf.download(tickers=tickers, period=period, interval=interval, group_by="ticker", auto_adjust=False, threads=True, progress=False)
    frames = []
    for t in tickers:
        tdf = data[t].reset_index().rename(columns={"Date":"date","Adj Close":"Adj Close","Volume":"Volume"})
        tdf["Ticker"] = t
        tdf["Daily Return"] = tdf["Adj Close"].pct_change()
        tdf["Rolling Volatility"] = tdf["Daily Return"].rolling(ROLL_WINDOW).std()
        tdf["Rolling Volatility Ann"] = tdf["Rolling Volatility"] * sqrt(252)
        tdf["Volume Change"] = tdf["Volume"].pct_change()
        frames.append(tdf[["date","Ticker","Adj Close","Volume","Daily Return","Rolling Volatility","Rolling Volatility Ann","Volume Change"]])
    return pd.concat(frames, ignore_index=True).dropna(subset=["Adj Close"])

def base_price(df):
    return df.groupby("Ticker")["Adj Close"].transform("first")

def index100(df):
    bp = base_price(df)
    return (df["Adj Close"] / bp) * 100

def drawdown_series(df):
    # per-ticker cumulative max and drawdown
    return df.groupby("Ticker").apply(lambda g: (g["Adj Close"] / g["Adj Close"].cummax()) - 1.0).reset_index(level=0, drop=True)

df = load_prices(TICKERS, PERIOD, INTERVAL)
min_d, max_d = df["date"].min(), df["date"].max()

with st.sidebar:
    st.header("Filters")
    tickers_sel = st.multiselect("Ticker", TICKERS, default=["MSFT","AAPL"])
    dr = st.slider("Date range", min_value=min_d.to_pydatetime(), max_value=max_d.to_pydatetime(), value=(max_d.to_pydatetime()-timedelta(days=120), max_d.to_pydatetime()))
    st.caption("Tip: Use Ctrl/Cmd-click to select multiple tickers.")

mask = (df["Ticker"].isin(tickers_sel)) & (df["date"] >= pd.Timestamp(dr[0])) & (df["date"] <= pd.Timestamp(dr[1]))
view = df.loc[mask].copy()
view["Index100"] = index100(view)
view["Drawdown"] = drawdown_series(view)

# KPIs
kpi_area = st.container()
col1, col2, col3 = kpi_area.columns(3)
latest = view.sort_values("date").groupby("Ticker").tail(1)
col1.metric("Last Daily Return", f"{latest['Daily Return'].mean():.2%}")
col2.metric("Rolling Vol (Ann)", f"{latest['Rolling Volatility Ann'].mean():.2%}")
col3.metric("Max Drawdown", f"{view.groupby('Ticker')['Drawdown'].min().mean():.2%}")

# Charts
lc = st.container()
st.subheader("Indexed to 100")
for t in tickers_sel:
    sub = view[view["Ticker"] == t]
    st.line_chart(sub.set_index("date")["Index100"], height=220)

st.subheader("Return vs Volatility")
scatter = view.groupby("Ticker").agg({"Daily Return":"mean","Rolling Volatility":"mean"}).rename(columns={"Daily Return":"Mean Return","Rolling Volatility":"Mean Vol"})
st.scatter_chart(scatter, x="Mean Vol", y="Mean Return", color="Ticker", height=220)

st.subheader("Raw rows (preview)")
st.dataframe(view.tail(200), use_container_width=True)

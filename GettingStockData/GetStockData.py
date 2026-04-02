# -*- coding: utf-8 -*-
"""
Stock Data Ingestion Script

This module downloads historical stock price data from Yahoo Finance for a
given list of tickers and stores the data locally as CSV files.

Overview
--------
- Reads a list of stock tickers from a JSON file.
- Downloads historical OHLCV (Open, High, Low, Close, Volume) data using yfinance.
- Cleans and standardizes the output format:
    * Removes MultiIndex columns if present
    * Converts the date index into a column
    * Ensures consistent column ordering
- Saves each ticker’s data as an individual CSV file in a centralized directory.

Data Output Format
------------------
Each CSV file is saved with the following structure:

    Date | Open | High | Low | Close | Adj Close | Volume

An index column is preserved to maintain compatibility with downstream
processing scripts.

Directory Structure
-------------------
The output files are stored in a root-level directory:

    project_root/
        ├── StockData/
        │   ├── AAPL.csv
        │   ├── MSFT.csv
        │   └── ...

The script automatically creates the `StockData` directory if it does not exist.

Author: Mike
"""

import json
import yfinance as yf
from pathlib import Path
import pandas as pd

#opens the file and gets the data inside
with open('symbol_1500.json') as f:
    daa = json.load(f)

def download_each_ticker_to_csv(tickers, start_date, end_date):
    """
    Downloads the Yahoo Finance data for a list of tickers.
    :param tickers: list[str]
    :param start_date: str
        Format: YYYY-MM-DD
    :param end_date: str
        Format: YYYY-MM-DD
    :return:
    """
    for ticker in tickers:
        base_path = Path(__file__).resolve().parent.parent

        #Creates StockData folder
        data_folder = base_path / "StockData"
        data_folder.mkdir(exist_ok=True)

        df = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            auto_adjust=False,
            progress=False,
        )
        # If yfinance returns MultiIndex columns, remove the ticker level
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Turn Date index into a normal column
        df = df.reset_index()

        expected_cols = ["Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"]
        df = df[expected_cols]

        if df.empty:
            print(f"Skipping {ticker} (no data)")
            continue

        file_path = data_folder / f"{ticker}.csv"
        df.to_csv(file_path, index=True)
        print(f"Saved {ticker}_data.csv")

download_each_ticker_to_csv(daa, "2021-01-01", "2021-12-31")
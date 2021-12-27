# -*- coding: utf-8 -*-
"""
Created on Wed Dec 15 19:33:16 2021

@author: Mike
"""

import time
import datetime
import pandas as pd
import json

#opens the file and gets the data inside
with open('symbol_1500.json') as f:
    daa = json.load(f)

#code taken from https://learndataanalysis.org/source-code-download-historical-stock-data-from-yahoo-finance-using-python/
for ticker in daa: #loops through the stock list and downloads the files (note: the website will throttle you)
    period1 = int(time.mktime(datetime.datetime(2021, 1, 1, 23, 59).timetuple()))
    period2 = int(time.mktime(datetime.datetime(2021, 12, 1, 23, 59).timetuple()))
    interval = '1d' # 1d, 1m

    query_string = f'https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={period1}&period2={period2}&interval={interval}&events=history&includeAdjustedClose=true'
    
    try:
        df = pd.read_csv(query_string)
        df.to_csv('{}.csv'.format(ticker))
    except:
        print(ticker)
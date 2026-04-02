# -*- coding: utf-8 -*-
"""
Linear Regression Momentum Strategy

This module implements a rule-based trading strategy that uses short-term
linear regression to estimate price trends (momentum) for a universe of stocks.
The slope of the fitted regression line is used as a signal to determine
buy and sell decisions.

Strategy Overview
-----------------
- For each stock, a rolling window of recent historical prices is extracted.
- A simple linear regression is fitted to the price series.
- The slope (trend) of the regression line is used as a momentum indicator:
    * Positive slope → upward trend (potential buy signal)
    * Negative slope → downward trend (potential sell signal)

- Portfolio decisions:
    * Stocks with slope above a buy threshold are purchased
    * Stocks with slope below a sell threshold are liquidated
    * Remaining stocks are held

Key Assumptions
---------------
- Fixed lookback window (e.g., 14 days) for regression
- Prices are taken directly from historical CSV data
- No transaction costs, slippage, or liquidity constraints
- Signals are recalculated at each rebalancing date
Author: Mike
"""
#import statements
import os
from csv import reader
import PortfolioFunctions as p
import numpy as np
from copy import deepcopy
from scipy.optimize import curve_fit
from typing import Dict, List, Tuple


def SellAndBuy(port: Dict[str, float], date: str, stock_list: List[str], date_list: List[str]) -> Tuple[Dict[str, float], List[float]]:
    """
    Rebalance the portfolio for a given trading date.

    This function computes the linear-regression slope for each eligible stock,
    uses those slope values as trading signals, sells positions with weak
    momentum, and buys positions with strong momentum.
    :param port: dict
        Current portfolio holdings and cash balance.
    :param date: str
        Current trading date in YYYY-MM-DD format.
    :param stock_list: list[str]
        List of stock CSV filenames available for evaluation.
    :param date_list: list[str]
        Master list of trading dates used by the backtest.

    :return:
    portfolio : dict
        Updated portfolio after selling and buying.
    :return:
    Stock_m_value : list[float]
        Linear-regression slope values for all valid stocks on the given date.
    """
    Stock_m_value, valid_stocks = LinRegressStocks(date, stock_list, date_list)

    port_copy = deepcopy(port)
    what_to_sell = sell_stocks(port_copy, Stock_m_value, valid_stocks)
    portfolio = p.selling(port_copy, date, what_to_sell)
    what_to_buy = buy_stocks(portfolio, Stock_m_value, valid_stocks)
    portfolio = p.buying(portfolio, date, what_to_buy, valid_stocks)

    return portfolio, Stock_m_value

def linear(a: float, x: np.ndarray, b: float) -> np.ndarray:
    """
    Linear function used for curve fitting.

    This is the model fitted to recent stock prices in order to estimate
    the short-term trend slope.
    :param a: float
        Slope coefficient.
    :param x: array-like
        Independent variable values.
    :param b: float
        Intercept coefficient.
    :return: array-like
        Predicted y-values from the linear model.
    """
    return a*x+b

def LinRegressStocks(
    date: str,
    stock_list: List[str],
    date_list: List[str]) -> Tuple[List[float], List[str]]:
    """
    Compute regression slope values for all stocks with sufficient history.

    For each stock in the input list, this function attempts to calculate
    a momentum score based on a linear regression over recent prices.
    Stocks with insufficient price history are skipped.
    :param date: str
        Current trading date in YYYY-MM-DD format.
    :param stock_list: list[str]
        List of stock CSV filenames to evaluate.
    :param date_list: list[str]
        Master list of trading dates used by the backtest.

    :return: tuple
    lst_of_m : list[float]
        Regression slope values for all valid stocks.
    valid_stocks : list[str]
        Stocks for which a valid slope value was successfully computed.
    """
    lst_of_m = []
    valid_stocks = []

    for stock in stock_list:
        m = regress(date, stock, date_list)
        if m is None:
            print(f"Skipping {stock}: insufficient history on {date}")
            continue

        lst_of_m.append(m)
        valid_stocks.append(stock)

    return lst_of_m, valid_stocks

def regress(
    date: str,
    stock: str,
    date_list: List[str]) -> float | None:
    """
    Fit a linear regression to recent prices for a single stock.

    The regression is performed on a fixed lookback window of historical
    prices ending at the specified date. The slope of the fitted line is
    used as a momentum indicator.
    :param date: str
        Current trading date in YYYY-MM-DD format.
    :param stock: str
        Stock CSV filename.
    :param date_list: list[str]
        Master list of trading dates used by the backtest.

    :return: float or None
        Slope of the fitted regression line. Returns None if there is not
        enough historical data to run the regression.
    """
    y_data = getPrices(date, stock, date_list)

    if y_data is None or len(y_data) < 14:
        return None

    x_data = np.linspace(1, len(y_data), len(y_data))
    p_opt, p_cov = curve_fit(linear, x_data, y_data, p0=(0, 0))
    return p_opt[0]
    
    
def getPrices(
    date: str,
    stock: str,
    date_list: List[str]) -> List[float] | None:
    """
    Retrieve the recent price history for a stock up to a target date.

    This function reads the stock's CSV file and attempts to collect a fixed
    number of historical prices prior to the input date. The resulting list
    is used as input for the regression model.
    :param date: str
        Current trading date in YYYY-MM-DD format.
    :param stock: str
        Stock CSV filename.
    :param date_list: list[str]
        Master list of trading dates used by the backtest.
    :return: list[float] or None
        List of historical prices for the stock. Returns None if the stock
        does not have enough data for the required lookback window.
    """
    price_history = [] #the price history of the stock
    dir_path = os.path.dirname(os.path.realpath(__file__))+"\\"+"StockData"+"\\"+stock
    with open(dir_path, "r") as f:
        lines = reader(f)
        days = 14 #number of days in the past we want to adjust
        start = date_list.index(date)-days #the integer can be adjusted as needed to get more or less price history
        flag = 0
        for l in lines: #looping through the lines
            if l[1] == date_list[start+flag] or flag!=0: #checking to see if the date matches the one needed
                try:
                    hold = float(l[2])
                except:
                    hold = -1
                price_history.append(hold) #appending the price
                flag+=1
                if flag == days: #if the number of days is met, return the price history
                    return price_history
            
def sell_stocks(
    port: Dict[str, float],
    Stock_m_value: List[float],
    stock_list: List[str]) -> List[int]:
    """
    Generate sell signals for current portfolio holdings.

    A stock is marked for sale when its regression slope falls below
    the configured sell threshold, indicating weak or negative momentum.
    :param port: dict
        Current portfolio holdings and cash balance.
    :param Stock_m_value: list[float]
        Regression slope values for valid stocks.
    :param stock_list: list[str]
        Stocks corresponding to the slope values.
    :return: list[int]
        Binary sell decisions for each stock currently held in the portfolio.
        A value of 1 indicates sell, and 0 indicates hold.
    """
    selling = []
    for stock in port: #looping through the portfolios holdings
        if stock!="cash":
            SellorHold = Stock_m_value[stock_list.index(stock)]
            if SellorHold <= -1: #if the a value is below a certain threshold sell
                selling.append(1)
            else:
                selling.append(0)
    return selling

def buy_stocks(
    port: Dict[str, float],
    Stock_m_value: List[float],
    stock_list: List[str]) -> List[int]:
    """
    Generate buy signals for eligible stocks.

    A stock is marked for purchase when its regression slope exceeds
    the configured buy threshold, indicating strong positive momentum.

    :param port: dict
        Current portfolio holdings and cash balance.
    :param Stock_m_value: list[float]
        Regression slope values for valid stocks.
    :param stock_list: list[str]
        Stocks corresponding to the slope values.
    :return: list[int]
        Binary buy decisions for each valid stock.
        A value of 1 indicates buy, and 0 indicates do not buy.
    """
    buying = []
    for i in range(len(stock_list)):
        SellorHold = Stock_m_value[i]
        if SellorHold > 1: #if the a value is above a certain threshold then buy
            buying.append(1)
        else:
            buying.append(0)
    return buying

    
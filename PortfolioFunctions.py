# -*- coding: utf-8 -*-
"""
Portfolio Utility Functions

This module provides shared portfolio-management utilities used across the
project's trading strategies. It includes helper functions for retrieving
historical stock prices, executing buy and sell operations, computing expected
portfolio returns, constructing fixed allocations, and valuing portfolio
holdings over time.

Purpose
-------
This file serves as the execution and valuation layer of the backtesting
framework. Strategy modules generate buy and sell signals, while this module
handles the mechanics of:
- Looking up historical prices from stored CSV data
- Updating portfolio positions after trades
- Tracking remaining cash balances
- Computing portfolio value on a given date

Key Responsibilities
--------------------
- Price retrieval from local stock data files
- Portfolio rebalancing through buy/sell operations
- Capital allocation for fixed-weight portfolios
- Portfolio valuation for both standard and Monte Carlo workflows

Author: Mike
"""
import os
from csv import reader

def stock_price(date: str, stock: str) -> str | None:
    """
    Retrieve the stock price for a given date from a local CSV file.
    :param date: str
        Trading date in YYYY-MM-DD format.
    :param stock: str
        Stock filename or identifier used in the StockData directory.
    :return: str or None
        Stock price as a string if found, otherwise None.
    """
    dir_path = os.path.dirname(os.path.realpath(__file__))+"\\"+"StockData"+"\\"+stock
    with open(dir_path, "r") as f:
        lines = reader(f)
        for l in lines: #looping through the rows
            if l[1] == date: #checking to see if the row matches the date wanted
                return l[2]

def selling(port: dict, date: str, what_to_sell: list[int]) -> dict:
    """
    Update the portfolio by selling selected stock holdings.

    For each stock flagged for sale, the function retrieves the stock price
    on the given date, converts the position into cash, and sets the number
    of shares held to zero.

    :param port: dict
        Portfolio containing holdings and cash balance.
    :param date: str
        Trading date used to retrieve stock prices.
    :param what_to_sell: list[int]
        Binary list indicating which stocks to sell (1 = sell, 0 = hold).
    :return: dict
        Updated portfolio after executing sell operations.
    """
    stocks = list(port.keys()) #list of ticker names
    for i in range(1,len(what_to_sell)): #loops through the list of tickers telling which to sell, starts at 1 since 0 is reserved for cash
        if what_to_sell[i]: #if the ticker is going to be sold
            try: #there are a lot of possibilities for why a stock price may not be properly retrieved like bankruptcy, this allows the program to continue running if that is the case
                price = float(stock_price(date, stocks[i])) #getting the price of the stock
                port["cash"] += port[stocks[i]]*price #updating the amount of cash
                port[stocks[i]] = 0 #setting number of shares of the stock to 0
            except:
                pass
    return port

def expectedReturns(returns: list[float], part: list[float]) -> float:
    """
    Compute the expected return of a portfolio given asset returns and weights.

    :param returns: list[float]
        Expected return values for each asset.
    :param part: list[float]
        Allocation weights or partition values.
    :return: float
        Weighted expected portfolio return.
    """
    expected_return = 0
    for i in range(len(part)):
        expected_return+=(part[i]/sum(part))*returns[i]
    return expected_return

def buying(port: dict, date: str, what_to_buy: list[int], stock_list: list[str]) -> dict:
    """
    Update the portfolio by purchasing selected stocks using available cash.

    Cash is split evenly across all selected stocks, and only whole shares
    are purchased.

    :param port: dict
        Portfolio containing holdings and cash balance.
    :param date: str
        Trading date used to retrieve stock prices.
    :param what_to_buy: list[int]
        Binary list indicating which stocks to buy (1 = buy, 0 = skip).
    :param stock_list: list[str]
        List of stock identifiers corresponding to buy signals.
    :return: dict
        Updated portfolio after executing buy operations.
    """
    stocks = list(port.keys()) #list of ticker names
    split = port["cash"]/sum(what_to_buy) #dividing the cash used to buy shares evenly
    for i in range(len(what_to_buy)): #loops through the list of tickers telling which to buy
        if what_to_buy[i]:#if the ticker is going to be bought
            try:  
                price = float(stock_price(date, stock_list[i]))
                number_of_shares = split//price #getting the number of shares that can be bought
                if stock_list[i] not in stocks: #checking to see if the dictionary entry exists
                    port[stock_list[i]] = 0
                port[stock_list[i]] += number_of_shares #adding the newly bought shares
                port["cash"] -= number_of_shares*price #reducing the cash 
            except:
                pass
    return port

def buyPermanent(date: str, date_list: list[str], stock_list: list[str], port: list[float], portfolio: dict) -> dict:
    """
    Construct a fixed-weight portfolio allocation.

    Each stock is allocated a percentage of the original portfolio cash,
    and the maximum number of whole shares is purchased.

    :param date: str
        Trading date used to retrieve stock prices.
    :param date_list: list[str]
        Master list of trading dates (not used directly).
    :param stock_list: list[str]
        List of available stocks.
    :param port: list[float]
        Allocation percentages for each stock (sums to 100).
    :param portfolio: dict
        Portfolio containing initial cash balance.
    :return: dict
        Updated portfolio after applying fixed allocation.
    """
    og_cash = portfolio["cash"]
    for i in range(len(port)):
        total_cash = og_cash*port[i]/100
        price = float(stock_price(date, stock_list[i]))
        number_of_shares = total_cash // price
        portfolio[stock_list[i]] = number_of_shares
        portfolio["cash"] -= price*number_of_shares
        
        if total_cash < price*number_of_shares:
            print("error")
            print(port, date, portfolio)
    return portfolio

def value(port: dict, date: str) -> float:
    """
    Compute the total value of a portfolio at a given date.

    This version expects a portfolio indexed by date.

    :param port: dict
        Dictionary of portfolio states indexed by date.
    :param date: str
        Trading date for valuation.
    :return: float
        Total portfolio value including cash and stock holdings.
    """
    total_val = 0 #total value of portfolio
    for stock in port[date]: #looping through the portfolio's holding on that date
        if stock == "cash": #checking to see if the holding is cash
            total_val += port[date][stock]
        else: #if it is not then it is a ticker
            try:
                price = float(stock_price(date, stock))
                if price == 0:
                    price = max()
                total_val += price * port[date][stock]
            except:
                pass
    return total_val

def valueMonte(port: dict, date: str) -> float:
    """
    Compute the total value of a portfolio for Monte Carlo simulations.

    This version expects a flat portfolio dictionary (not date-indexed).

    :param port: dict
        Portfolio containing holdings and cash balance.
    :param date: str
        Trading date for valuation.
    :return: float
        Total portfolio value including cash and stock holdings.
    """
    total_val = 0 #total value of portfolio
    for stock in port: #looping through the portfolio's holding on that date
        if stock == "cash": #checking to see if the holding is cash
            total_val += port[stock]
        else: #if it is not then it is a ticker
            try:
                price = float(stock_price(date, stock))
                if price == 0:
                    price = max()
                total_val += price * port[stock]
            except:
                pass
    return total_val
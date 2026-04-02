# -*- coding: utf-8 -*-
"""
Random Trading Strategy

This module implements a naive benchmark strategy that makes random buy and
sell decisions across a stock universe. At each rebalance step, the algorithm
randomly decides which currently held assets to sell and which available assets
to buy.

Purpose
-------
This strategy is intended as a baseline for comparison against more structured
trading approaches. Because the portfolio decisions are random, it provides a
useful reference point for evaluating whether signal-based strategies add value
beyond chance.

Key Assumptions
---------------
- Buy and sell decisions are made independently at random.
- Each stock has an equal probability of being selected or ignored.
- No transaction costs, slippage, or liquidity constraints are considered.
- The random seed is fixed for reproducibility across runs.

Author: Mike
"""

import random
import PortfolioFunctions as p
from copy import deepcopy

random.seed(2008) #the seed for the random number

def Sell(
    port: dict[str, float],
    date: str,
    stock_list: list[str]) -> dict[str, float]:
    """
    Randomly select current holdings to sell and update the portfolio.
    :param port: dict
        Current portfolio holdings and cash balance.
    :param date: str
        Current trading date.
    :param stock_list: list[str]
        List of available stocks. Included for interface consistency.
    :return: dict
        Updated portfolio after executing random sell decisions.
    """
    what_to_sell = sell_stocks(port) #getting the list of what stocks will be sold
    port_copy = deepcopy(port)
    portfolio = p.selling(port_copy, date, what_to_sell) #updates the portfolio
    return portfolio

def Buy(
    port: dict[str, float],
    date: str,
    stock_list: list[str]) -> dict[str, float]:
    """
    Randomly select stocks to buy and update the portfolio.
    :param port: dict
        Current portfolio holdings and cash balance.
    :param date: str
        Current trading date.
    :param stock_list: list[str]
        List of available stocks that may be purchased.
    :return: dict
        Updated portfolio after executing random buy decisions.
    """
    what_to_buy = buy_stocks(stock_list) #decides on what to buy
    port_copy = deepcopy(port)
    portfolio = p.buying(port_copy, date, what_to_buy, stock_list) #updates the portfolio
    return portfolio

def sell_stocks(port: dict[str, float]) -> list[int]:
    """
    Generate random sell signals for the current portfolio holdings.

    Each holding receives a binary decision:
    - 1 = sell
    - 0 = hold
    :param port: dict
        Current portfolio holdings.
    :return: list[int]
        Binary list of sell decisions for the portfolio holdings.
    """
    selling = []
    for stock in port: #looping through the stocks in the portfolio
        SellorHold = random.randint(0,1) #randomly choosing whether to sell
        if SellorHold:
            selling.append(1)
        else:
            selling.append(0)
    return selling

def buy_stocks(stock_list: list[str]) -> list[int]:
    """
    Generate random buy signals for the available stock universe.

    Each stock receives a binary decision:
    - 1 = buy
    - 0 = do not buy
    :param stock_list: list[str]
        List of available stocks.
    :return: list[int]
        Binary list of buy decisions for each stock.
    """
    buying = []
    for stock in stock_list: #looping through the stocks in the portfolio
        BuyorHold = random.randint(0,1) #randomly choosing whether to buy
        if BuyorHold:
            buying.append(1)
        else:
            buying.append(0)
    return buying
    


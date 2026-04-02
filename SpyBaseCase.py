# -*- coding: utf-8 -*-
"""
SPY Baseline Strategy

This module implements a simple benchmark trading strategy that allocates
100% of the portfolio capital to SPY (the S&P 500 ETF) at every rebalancing step.

Purpose
-------
This serves as a baseline comparison for more complex strategies (e.g.,
momentum-based or regression-driven models). By comparing performance against
this "buy SPY only" strategy, we can evaluate whether more advanced approaches
add value over a passive market exposure.

Key Assumptions
---------------
- The portfolio is rebalanced at each time step.
- All available capital is invested in SPY.
- No transaction costs or slippage are considered.
- The stock universe includes "SPY.csv".

Author: Mike
"""
import PortfolioFunctions as p
from copy import deepcopy

def Sell(
    port: dict[str, float],
    date: str,
    stock_list: list[str]) -> dict[str, float]:
    """
    Sell step of the SPY baseline strategy.

    This strategy does not actively sell any positions, as it is designed
    to maintain full allocation to SPY at all times.
    :param port: dict
        Current portfolio holdings and cash balance.
    :param date: str
        Current trading date (unused in this strategy).
    :param stock_list: list[str]
        List of available stocks (unused in this function).
    :return: dict
        Unmodified portfolio (no selling occurs).
    """
    return port

def Buy(
    port: dict[str, float],
    date: str,
    stock_list: list[str]) -> dict[str, float]:
    """
    Buy step of the SPY baseline strategy.

    Allocates capital exclusively to SPY by generating a buy signal
    for SPY and no other assets.
    :param port: dict
        Current portfolio holdings and cash balance.
    :param date: str
        Current trading date.
    :param stock_list: list[str]
        List of available stock CSV filenames.
    :return: dict
        Updated portfolio after executing buy orders.
    """
    what_to_buy = buy_stocks(stock_list)
    port_copy = deepcopy(port)
    portfolio = p.buying(port_copy, date, what_to_buy, stock_list)
    return portfolio


def buy_stocks(stock_list: list[str]) -> list[int]:
    """
    Generate buy signals for the SPY-only strategy.

    This function creates a binary signal vector indicating which assets
    should be purchased. Only SPY receives a buy signal.
    :param stock_list: list[str]
        List of stock CSV filenames (e.g., ["AAPL.csv", "SPY.csv"]).
    :return: list[int]
        Binary list where:
        - 1 indicates the stock should be bought
        - 0 indicates no action
    """
    buying = []
    for stock in stock_list:
        if stock == "SPY.csv":
            buying.append(1)
        else:
            buying.append(0)
    return buying
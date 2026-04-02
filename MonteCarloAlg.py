# -*- coding: utf-8 -*-
"""
Monte Carlo Portfolio Strategy

This module implements a portfolio-construction strategy that uses recent
historical stock behavior to simulate a large number of candidate portfolios.
Each simulated portfolio is evaluated using expected return and estimated risk,
and can then be ranked using a Sharpe-ratio-style metric.

Strategy Overview
-----------------
- Compute recent daily log returns for each stock
- Estimate mean returns and covariance structure from a rolling lookback window
- Randomly generate many portfolio weight combinations
- Simulate the resulting portfolios
- Compare portfolios using return and risk metrics

Purpose
-------
This file is designed as an experimental quantitative trading module within a
broader backtesting framework. It demonstrates how Monte Carlo simulation can
be used to explore the portfolio-allocation space instead of selecting assets
using a fixed deterministic rule.

Author: Mike
"""
#import statements
import random
import PortfolioFunctions as p
from typing import Dict, List, Tuple
import numpy as np
from copy import deepcopy
from random import randint, shuffle

random.seed(2008) #setting the random seed
days_back = 7 #how many days back the algorithm will check

def dailyReturns(
    date: str,
    date_list: List[str],
    stock: str) -> float:
    """
    Compute the daily log return for a stock on a given date.

    The return is calculated using the stock price on the current date and
    the previous trading date in the master date list.
    :param date: str
        Current trading date.
    :param date_list: list[str]
        Ordered list of all trading dates in the backtest.
    :param stock: str
        Stock identifier or filename.
    :return: float
        Daily log return for the stock.
    """
    present_price = float(p.stock_price(date, stock))
    yesterday_price = float(p.stock_price(date_list[date_list.index(date)-1], stock))
    return np.log(present_price/yesterday_price)

def StockReturns(
    date: str,
    date_list: List[str],
    stock_list: List[str]) -> Dict[str, List[float]]:
    """
    Build a return history dictionary for all stocks over the lookback window.

    For each stock, this function collects daily log returns over the most
    recent `days_back` trading days prior to the input date.
    :param date: str
        Current trading date.
    :param date_list: list[str]
        Ordered list of all trading dates in the backtest.
    :param stock_list: list[str]
        List of stocks to evaluate.
    :return: dict[str, list[float]]
        Dictionary mapping each stock to a list of recent daily log returns.
    """
    start_date = date_list.index(date)-days_back
    stock_returns = {}
    for day in date_list[start_date:start_date+days_back]:
        for stock in stock_list: #looping through the list of stocks
            if stock not in stock_returns:
                stock_returns[stock] = []
            stock_returns[stock].append(dailyReturns(day, date_list, stock)) #finding and appending daily return
    return stock_returns

def meanReturn(returns: List[float]) -> float:
    """
    Compute the arithmetic mean of a return series.
    :param returns: list[float]
        Sequence of return observations.
    :return: float
        Average return over the sample window.
    """
    total_r = 0
    for r in returns:
        total_r +=r
    return total_r / len(returns)

def create_covar(
    date: str,
    date_list: List[str],
    stock_list: List[str]) -> np.ndarray:
    """
    Estimate a covariance-like matrix using recent stock prices.

    This function collects recent historical prices for each stock, centers
    each series by subtracting its mean, and then computes a matrix based on
    the dot product of the centered price matrix.
    :param date: str
        Current trading date.
    :param date_list: list[str]
        Ordered list of all trading dates in the backtest.
    :param stock_list: list[str]
        List of stocks to include in the covariance estimate.
    :return: numpy.ndarray
        Covariance-style matrix used as a risk input for portfolio evaluation.
    """
    stock_prices = []
    start_date = date_list.index(date)-days_back
    counter = 0
    for stock in stock_list: #looping through the stock list
        stock_price = []
        for day in date_list[start_date:start_date+days_back]: #looping through the date list
            stock_price.append(float(p.stock_price(day, stock))) #appending the price of the stock on that day
            counter+=1 #counting the number of elements
        mean_price = np.mean(stock_price) #getting the mean price of the stock
        stock_price = stock_price - mean_price #subtracting it from the array
        stock_prices.append(stock_price)
    stock_prices = np.array(stock_prices)
    transpose_stock_prices = stock_prices.transpose() #transposing the matrix
    covariance = stock_prices.dot(transpose_stock_prices) #multiplying the matrices together
    return covariance / counter
    
def calculate_volatility(
    covariant: np.ndarray,
    weightings: List[List[float]]) -> np.ndarray:
    """
    Estimate relative portfolio volatility for a set of candidate weight vectors.

    Each candidate portfolio is normalized into weights that sum to 1, then
    evaluated using the covariance matrix. The resulting variance estimates are
    scaled relative to the largest variance before taking the square root.
    :param covariant: numpy.ndarray
        Covariance-style matrix of stock relationships.
    :param weightings: weightings : list[list[float]]
        Candidate portfolio allocations.
    :return: numpy.ndarray
        Relative volatility values for the candidate portfolios.
    """
    variance_list = []
    for weight_vec in weightings: #loops through the weightings of the matrix
        hold = np.array(weight_vec) / sum(weight_vec) #properly weighting the vector
        hold_2 = hold.transpose() #transposing the vector
        first_calc = hold.dot(covariant) #doing the dot product with vector and covariant matrix
        final_calc = first_calc.dot(hold_2) #dot product with vector and covariant matrix
        variance_list.append(final_calc) #appending it to the list
    return np.sqrt(variance_list/max(variance_list))

def simulate_port(
    date: str,
    date_list: List[str],
    stock_list: List[str],
    portfolio: Dict[str, Dict[str, float]]) -> Tuple[List[Dict[str, float]], List[List[int]]]:
    """
    Generate and simulate a large set of candidate portfolios.

    This function randomly samples portfolio allocations, adds an equal-weight
    baseline portfolio, and then constructs the corresponding portfolio objects
    using the project's shared portfolio utility functions.
    :param date: str
        Current trading date.
    :param date_list: list[str]
        Ordered list of all trading dates in the backtest.
    :param stock_list: list[str]
        List of stocks available for allocation.
    :param portfolio: dict
        Portfolio history or state container used by the backtest.
    :return: tuple
        portfolio_possibilities : list
            Simulated portfolio objects.
        portfolio_partitions : list[list[int]]
            Integer allocation partitions used to generate the portfolios.
    """
    portfolio_partitions = []
    portfolio_possibilities = []
    for i in range(10000): #the number of portfolios being made
        portfolio_partitions.append(createPartitions(100, len(stock_list))) #randomly generating portfolio
    portfolio_partitions.append([100/len(stock_list)]*len(stock_list)) #equally divided portfolio
    for port in portfolio_partitions: #looping through newly generated porfolios
        portfolio_possibilities.append(p.buyPermanent(date, date_list, stock_list, port, deepcopy(portfolio[date])))
    return portfolio_possibilities, portfolio_partitions

def calc_sharpe(
    returns: List[float],
    risk: List[float]) -> List[float]:
    """
    Compute a simplified Sharpe-style ratio for candidate portfolios.

    This implementation divides return by risk directly and does not subtract
    a risk-free rate.
    :param returns: list[float]
        Portfolio return values.
    :param risk: list[float]
        Portfolio risk values.
    :return: list[float]
        Return-to-risk ratios for the candidate portfolios.
    """
    sharpe = []
    for i in range(len(returns)):
        sharpe.append(returns[i]/risk[i])
    return sharpe

def createPartitions(
    total: int,
    groups: int) -> List[int]:
    """
    Randomly partition an integer total across a fixed number of groups.

    This function is used to generate discrete candidate portfolio allocations
    whose weights sum to a fixed total (e.g., 100 units of capital).
    :param total: int
        Total amount to allocate.
    :param groups: int
        Number of allocation buckets.
    :return: list[int]
        Randomized allocation vector whose elements sum to `total`.
    """
    group = []
    for x in range(groups): #looping through the total number of integers
        group.append(randint(0, total-sum(group)-groups+x)) #generating a random interger
    if sum(group) != total: #making sure that the list sums up to the total
        group[-1] += total-sum(group)
    shuffle(group) #shuffling the list to maintain uniform distribution
    return group
    
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 17 15:36:40 2021

@author: Mike
"""

"""
This program simulates a trading algorithm which uses Monte Carlo simulation
on the stocks to determine which to buy and sell and records profits and losses
"""
#import statements
import time
import datetime
import pandas as pd
import json
import os
from csv import reader
import random
import PortfolioFunctions as p
import numpy as np
from copy import deepcopy
from random import randint, shuffle

random.seed(2008) #setting the random seed
days_back = 7 #how many days back the algorithm will check

def dailyReturns(date, date_list, stock): #returns the daily returns of the price of the stock
    present_price = float(p.stock_price(date, stock))
    yesterday_price = float(p.stock_price(date_list[date_list.index(date)-1], stock))
    return np.log(present_price/yesterday_price)

def StockReturns(date, date_list, stock_list): #fetching the stock returns of each stock 
    start_date = date_list.index(date)-days_back
    stock_returns = {}
    for day in date_list[start_date:start_date+days_back]:
        for stock in stock_list: #looping through the list of stocks
            if stock not in stock_returns:
                stock_returns[stock] = []
            stock_returns[stock].append(dailyReturns(day, date_list, stock)) #finding and appending daily return
    return stock_returns

def meanReturn(returns): #calculating the mean returns
    total_r = 0
    for r in returns:
        total_r +=r
    return total_r / len(returns)

def create_covar(date, date_list, stock_list): #creating the covariance matrix
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
    
def calculate_volatility(covariant, weightings): #calculate the volatility of the portfolios
    variance_list = []
    for weight_vec in weightings: #loops through the weightings of the matrix
        hold = np.array(weight_vec) / sum(weight_vec) #properly weighting the vector
        hold_2 = hold.transpose() #transposing the vector
        first_calc = hold.dot(covariant) #doing the dot product with vector and covariant matrix
        final_calc = first_calc.dot(hold_2) #dot product with vector and covariant matrix
        variance_list.append(final_calc) #appending it to the list
    return np.sqrt(variance_list/max(variance_list))

def simulate_port(date, date_list, stock_list, portfolio): #creates portfolios
    portfolio_partitions = []
    portfolio_possibilities = []
    for i in range(10000): #the number of portfolios being made
        portfolio_partitions.append(createPartitions(100, len(stock_list))) #randomly generating portfolio
    portfolio_partitions.append([100/len(stock_list)]*len(stock_list)) #equally divided portfolio
    for port in portfolio_partitions: #looping through newly generated porfolios
        portfolio_possibilities.append(p.buyPermanent(date, date_list, stock_list, port, deepcopy(portfolio[date])))
    return portfolio_possibilities, portfolio_partitions

def calc_sharpe(returns, risk): #calculating the sharpe ratio
    sharpe = []
    for i in range(len(returns)):
        sharpe.append(returns[i]/risk[i])
    return sharpe

def createPartitions(total, groups): #randomly generating partitions
    group = []
    for x in range(groups): #looping through the total number of integers
        group.append(randint(0, total-sum(group)-groups+x)) #generating a random interger
    if sum(group) != total: #making sure that the list sums up to the total
        group[-1] += total-sum(group)
    shuffle(group) #shuffling the list to maintain uniform distribution
    return group
    
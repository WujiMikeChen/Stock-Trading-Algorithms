# -*- coding: utf-8 -*-
"""
Created on Thu Dec 16 16:33:02 2021

@author: Mike
"""

"""
This program simulates a trading algorithm which uses linear regression on the stocks to determine which to buy
and records profits and losses
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
from scipy.optimize import curve_fit


def SellAndBuy(port, date, stock_list, date_list): #adjusts the portfolio
    Stock_m_value = LinRegressStocks(date, stock_list, date_list) #finding the a values for all the stocks
    port_copy = deepcopy(port) #copying the portfolio so no mutation occurs
    what_to_sell = sell_stocks(port_copy, Stock_m_value, stock_list) #determines the stocks to sell
    portfolio = p.selling(port_copy, date, what_to_sell) #adjusts the portfolio by selling
    what_to_buy = buy_stocks(portfolio, Stock_m_value, stock_list) #determines the stocks to buy
    portfolio = p.buying(portfolio, date, what_to_buy, stock_list) #adjusts the portfolio by buying
    return portfolio, Stock_m_value

def linear(a,x,b): #the function linear regression is being performed on
    return a*x+b

def LinRegressStocks(date, stock_list, date_list): #gets the list of a values for each stock
    lst_of_m = []
    for stock in stock_list: #looping through the stock list
        lst_of_m.append(regress(date, stock, date_list))
    return lst_of_m

def regress(date, stock, date_list): #performs linear regression on the stock data
    y_data = getPrices(date, stock, date_list)
    x_data = np.linspace(1,len(y_data), len(y_data))
    p_opt, p_cov = curve_fit(linear, x_data, y_data, p0=(0, 0))
    return p_opt[0]
    
    
def getPrices(date, stock, date_list): #returns a list of the prices of the stock
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
            
def sell_stocks(port, Stock_m_value, stock_list): #determines whether to sell the stock or not
    selling = []
    for stock in port: #looping through the portfolios holdings
        if stock!="cash":
            SellorHold = Stock_m_value[stock_list.index(stock)]
            if SellorHold <= -1: #if the a value is below a certain threshold sell
                selling.append(1)
            else:
                selling.append(0)
    return selling

def buy_stocks(port, Stock_m_value, stock_list): #determines whether to buy the stock or not
    buying = []
    for i in range(len(stock_list)):
        SellorHold = Stock_m_value[i]
        if SellorHold > 1: #if the a value is above a certain threshold then buy
            buying.append(1)
        else:
            buying.append(0)
    return buying

    
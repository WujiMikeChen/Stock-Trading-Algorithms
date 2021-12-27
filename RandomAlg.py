# -*- coding: utf-8 -*-
"""
Created on Wed Dec 15 18:53:59 2021

@author: Mike
"""

"""
This program simulates a trading algorithm which randomly picks stocks out of a list
and records profits and losses
"""
import time
import datetime
import pandas as pd
import json
import os
import random
import PortfolioFunctions as p
from copy import deepcopy

random.seed(2008) #the seed for the random number

def Sell(port, date, stock_list): #takes a portfolio and returns an updated one with the decided holdings sold
    what_to_sell = sell_stocks(port) #getting the list of what stocks will be sold
    port_copy = deepcopy(port)
    portfolio = p.selling(port_copy, date, what_to_sell) #updates the portfolio
    return portfolio

def Buy(port, date, stock_list): #takes a portfolio and returns an updated one after buying stocks
    what_to_buy = buy_stocks(stock_list) #decides on what to buy
    port_copy = deepcopy(port)
    portfolio = p.buying(port_copy, date, what_to_buy, stock_list) #updates the portfolio
    return portfolio

def sell_stocks(port): #algorithm determining whether to sell a stock or not
    selling = []
    for stock in port: #looping through the stocks in the portfolio
        SellorHold = random.randint(0,1) #randomly choosing whether to sell
        if SellorHold:
            selling.append(1)
        else:
            selling.append(0)
    return selling

def buy_stocks(stock_list): #algorithm determining whether to buy a stock or not
    buying = []
    for stock in stock_list: #looping through the stocks in the portfolio
        BuyorHold = random.randint(0,1) #randomly choosing whether to buy
        if BuyorHold:
            buying.append(1)
        else:
            buying.append(0)
    return buying
    


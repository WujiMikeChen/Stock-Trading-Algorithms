# -*- coding: utf-8 -*-
"""
Created on Thu Dec 16 16:09:08 2021

@author: Mike
"""

"""
This program simulates a trading algorithm which puts all the money into the stock SPY
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

def Sell(port, date, stock_list): #determines what stocks to sell and updates(none of them)
    return port

def Buy(port, date, stock_list): #determines what stocks to buy and updates portfolio
    what_to_buy = buy_stocks(stock_list)
    port_copy = deepcopy(port)
    portfolio = p.buying(port_copy, date, what_to_buy, stock_list)
    return portfolio


def buy_stocks(stock_list): #decides what stocks to buy
    buying = []
    for stock in stock_list:
        if stock == "SPY.csv":
            buying.append(1)
        else:
            buying.append(0)
    return buying
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 15 21:33:05 2021

@author: Mike
"""

"""
This program contains the basic functions every portfolio needs such as buying and selling stocks,
valuing stocks, and calculating expected returns
"""
import os
import time
import datetime
import pandas as pd
import json
from csv import reader
from datetime import timedelta, datetime

def stock_price(date, stock): #returns the price of the stock at the given date
    dir_path = os.path.dirname(os.path.realpath(__file__))+"\\"+"StockData"+"\\"+stock
    with open(dir_path, "r") as f:
        lines = reader(f)
        for l in lines: #looping through the rows
            if l[1] == date: #checking to see if the row matches the date wanted
                return l[2]

def selling(port, date, what_to_sell): #returns an updated portfolio after selling the stocks that were passed in
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

def expectedReturns(returns, part): #returns the expected returns
    expected_return = 0
    for i in range(len(part)):
        expected_return+=(part[i]/sum(part))*returns[i]
    return expected_return

def buying(port, date, what_to_buy, stock_list):#returns an updated portfolio after buying the stocks that were passed in
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

def buyPermanent(date, date_list, stock_list, port, portfolio): #buying portfolio algorithm for monte carlo
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

def value(port, date): #returns the value of the portfolio's holdings at the passed in date
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

def valueMonte(port, date): #returns the value of the portfolio's holdings at the passed in date
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
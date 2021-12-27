# -*- coding: utf-8 -*-
"""
Created on Wed Dec 15 19:34:26 2021

@author: Mike
"""

"""
This file controls all other files and performs the main simulation of 6 months for each
portfolio. It also plots the data and produces the output needed for all the questions.
"""
#import statements
import os
import time
import datetime
import pandas as pd
import json
from csv import reader
from datetime import date, timedelta, datetime
import RandomAlg as r
import PortfolioFunctions as func
import SpyBaseCase as spy
import numpy as np
import matplotlib.pyplot as plt
import LinearRegressionAlg as lin
import MonteCarloAlg as monte
import time

plt.rcParams["figure.figsize"] = [10,6] #setting the figure size
start = time.perf_counter() #starting the timer

stock_list = os.listdir("./StockData") #the list of all stocks
date_list = [] #the list of the dates from the start of the portfolio to the end
total_date_list = [] #the list of all dates when the stock exchange was open

start_date = date(2021, 6, 1).strftime("%Y-%m-%d") #the starting date of the portfolios
end_date = date(2021, 12, 1).strftime("%Y-%m-%d") #the ending date of the portfolios
delta = timedelta(days=1) #how much time moves forward each day

#this loop gets all the days where the stock exchange is open
dir_path = os.path.dirname(os.path.realpath(__file__))+"\\"+"StockData"+"\\"+"AAPL.csv"
with open(dir_path, "r") as f:
    next(f)
    lines = reader(f)
    for l in lines: #looping through the rows
        if start_date <= l[1] <= end_date:
            date_list.append(l[1])
        total_date_list.append(l[1])
    date_list.pop(0)
    total_date_list.pop(0)

first_day = (datetime.strptime(date_list[0],"%Y-%m-%d")-delta).strftime("%Y-%m-%d") #the first day of the portfolio
last_index = first_day #used for indexing purposes

#the portfolio for the random algorithm
RandomPortfolio = {}
RandomPortfolio[first_day] = {"cash": 100000}
value_Random = []

#the portfolio for the SPY algorithm
SPYPortfolio = {}
SPYPortfolio[first_day] = {"cash": 100000}
value_SPY = []

#the portfolio for the linear regression algorithm
LinRegressionPortfolio = {}
LinRegressionPortfolio[first_day] = {"cash": 100000}
value_Regression = []
price_history_apple = []
m_value_apple = []

#Monte carlo simulation portfolios

#3.a)
days_back = 7 #the number of days back the algorithm will process
monte_stock_list = ["AAPL.csv", "SPY.csv", "AMD.csv", "DOCU.csv", "CRSR.csv"] #stock list for monte carlo simulations
stock_returns = monte.StockReturns(date_list[42], date_list, monte_stock_list) #getting the returns

#plotting the data for 3a
plt.plot(date_list[42-days_back:42], stock_returns["AAPL.csv"], color = "r", label = "AAPL")
plt.plot(date_list[42-days_back:42], stock_returns["SPY.csv"], color = "b", label = "SPY")
plt.plot(date_list[42-days_back:42], stock_returns["AMD.csv"], color = "y", label = "AMD")
plt.plot(date_list[42-days_back:42], stock_returns["DOCU.csv"], color = "g", label = "DOCU")
plt.plot(date_list[42-days_back:42], stock_returns["CRSR.csv"], color = "m", label = "CRSR")
plt.xlabel("Date")
plt.xticks(np.arange(0,len(date_list[42-days_back:42]),2));
plt.ylabel("Stock Returns")
plt.legend()
plt.title("Daily Stock returns over time (Question 3a)")
plt.show()

#3.b)
MontePortfolio = {} #portfolio holding the values for the monte carlo portfolios
MontePortfolio[first_day] = {"cash": 100000}
#getting the partitions and portfolios
monte_portfolio, partitions = monte.simulate_port(last_index, total_date_list, monte_stock_list, MontePortfolio)
#creating example portfolios that were randomly generated
example_port_1 = []
example_port_2 = []
example_port_3 = []

#portfolios that take the expected returns and extrapolate
theoretical_port_1 = [100000]
theoretical_port_2 = [100000]
theoretical_port_3 = [100000]

#3c
#getting the return history of each stock
stock_returns = monte.StockReturns(last_index, total_date_list, monte_stock_list)

#getting the mean stock return of each stock
mean_stock_returns = []
for returns in stock_returns:
    mean_stock_returns.append(monte.meanReturn(stock_returns[returns]))

#getting the mean portfolio return 
mean_port_returns = []
for part in partitions:
    mean_port_returns.append(func.expectedReturns(mean_stock_returns, part))

#getting the covariance matrix
covariance_matrix = monte.create_covar(last_index, total_date_list, monte_stock_list)
#Getting the standard deviation of each portfolio
variance_list = monte.calculate_volatility(covariance_matrix, partitions)

#getting the sharpe ratio of each portfolio
sharpe_ratio = monte.calc_sharpe(np.array(mean_port_returns)*100, variance_list)

best_port = max(sharpe_ratio) #the highest sharp ratio
worst_port = min(sharpe_ratio) #the lowest sharp ratio
safest_port = sharpe_ratio[variance_list.tolist().index(min(variance_list))] #the portfolio with the lowest risk
equal_split = sharpe_ratio[-1] #the portfolio that had been equally diversified

best_port_value = []
worst_port_value = []
safest_port_value = []
equal_split_value = []

variance_list = variance_list.tolist()

#plotting the risk risk to return plots
plt.scatter(variance_list, np.array(mean_port_returns)*100, label = "Random portfolios", s= 1)
plt.scatter(variance_list[sharpe_ratio.index(best_port)], (np.array(mean_port_returns)*100)[sharpe_ratio.index(best_port)], color = "r", label = "Highest sharpe ratio: {}".format(round(best_port,4)), s = 80)
plt.scatter(variance_list[sharpe_ratio.index(worst_port)], (np.array(mean_port_returns)*100)[sharpe_ratio.index(worst_port)], color = "y", label = "Lowest sharpe ratio: {}".format(round(worst_port,4)), s= 80 )
plt.scatter(variance_list[sharpe_ratio.index(safest_port)], (np.array(mean_port_returns)*100)[sharpe_ratio.index(safest_port)],color = "m", label = "Lowest risk: {}".format(round(safest_port,4)), s=80)
plt.scatter(variance_list[-1], (np.array(mean_port_returns)*100)[-1], color = "g", label =  "Equal division: {}".format(round(equal_split,4)), s=80)
plt.xlabel("Portfolio Standard Deviation")
plt.legend(loc = "upper left")
plt.ylabel("Returns (%)")
plt.title("Portfolio risk-return Question (3c)")
plt.show()

#main chunk of the program, this loops through the days and simulates how each algorithm
#will react and change to the market
for i in range(len(date_list)): #looping through the business days
    #updating random portfolio
    RandomPortfolio[date_list[i]] = r.Sell(RandomPortfolio[last_index], date_list[i], stock_list)
    RandomPortfolio[date_list[i]] = r.Buy(RandomPortfolio[date_list[i]], date_list[i], stock_list)
    value_Random.append(func.value(RandomPortfolio, date_list[i]))
    
    #updating SPY portfolio
    SPYPortfolio[date_list[i]] = spy.Sell(SPYPortfolio[last_index], date_list[i], stock_list)
    SPYPortfolio[date_list[i]] = spy.Buy(SPYPortfolio[date_list[i]], date_list[i], stock_list)
    value_SPY.append(func.value(SPYPortfolio, date_list[i]))
    
    #updating Linear regression portfolio
    LinRegressionPortfolio[date_list[i]], m_value = lin.SellAndBuy(LinRegressionPortfolio[last_index], date_list[i], stock_list, total_date_list)
    value_Regression.append(func.value(LinRegressionPortfolio, date_list[i]))
    price_history_apple.append(float(func.stock_price(date_list[i], "AAPL.csv")))
    m_value_apple.append(m_value[stock_list.index("AAPL.csv")])
    
    #MonteCarloPortfolio
    #3b
    example_port_1.append(func.valueMonte(monte_portfolio[3], date_list[i]))
    example_port_2.append(func.valueMonte(monte_portfolio[1], date_list[i]))
    example_port_3.append(func.valueMonte(monte_portfolio[2], date_list[i]))
    
    theoretical_port_1.append(theoretical_port_1[-1]*(1+mean_port_returns[3]))
    theoretical_port_2.append(theoretical_port_2[-1]*(1+mean_port_returns[1]))
    theoretical_port_3.append(theoretical_port_3[-1]*(1+mean_port_returns[2]))
    
    #3c
    best_port_value.append(func.valueMonte(monte_portfolio[sharpe_ratio.index(best_port)], date_list[i]))
    worst_port_value.append(func.valueMonte(monte_portfolio[sharpe_ratio.index(worst_port)], date_list[i]))
    safest_port_value.append(func.valueMonte(monte_portfolio[sharpe_ratio.index(safest_port)], date_list[i]))
    equal_split_value.append(func.valueMonte(monte_portfolio[-1], date_list[i]))
    #updating the day
    last_index = (date_list[i])

theoretical_port_1.pop() #popping the unnecesary data points
theoretical_port_2.pop()
theoretical_port_3.pop()

example_port_1_txt = ""
example_port_2_txt = ""
example_port_3_txt = ""
for i in range(len(partitions[3])): #creating a string to make legend labels more legible
    example_port_1_txt = example_port_1_txt + str(partitions[3][i]) + "% " + monte_stock_list[i] + " "
    example_port_2_txt = example_port_2_txt + str(partitions[1][i]) + "% " + monte_stock_list[i] + " "
    example_port_3_txt = example_port_3_txt + str(partitions[2][i]) + "% " + monte_stock_list[i] + " "



#plotting all the data obtained from the simulation
    
#plotting question 3b
plt.plot(date_list, example_port_1, label = "{}".format(example_port_1_txt))
plt.plot(date_list, example_port_2, label = "{}".format(example_port_2_txt))
plt.plot(date_list, example_port_3, label = "{}".format(example_port_3_txt))
plt.xlabel("Date")
plt.ylabel("Value (dollars)")
plt.xticks(np.arange(0,len(date_list),40));
plt.legend()
plt.title("Portfolio Value over time using Monte Carlo method (3b)")
plt.show()

#plotting question 3b with theoretical returns
plt.plot(date_list[0:20], example_port_1[0:20], label = "{}".format(example_port_1_txt))
plt.plot(date_list[0:20], example_port_2[0:20], label = "{}".format(example_port_2_txt))
plt.plot(date_list[0:20], example_port_3[0:20], label = "{}".format(example_port_3_txt))
plt.plot(date_list[0:20], theoretical_port_1[0:20], label = "Theoretical {}".format(example_port_1_txt))
plt.plot(date_list[0:20], theoretical_port_2[0:20], label = "Theoretical {}".format(example_port_2_txt))
plt.plot(date_list[0:20], theoretical_port_3[0:20], label = "Theoretical {}".format(example_port_3_txt))
plt.xlabel("Date")
plt.ylabel("Value (dollars)")
plt.xticks(np.arange(0,len(date_list[0:20]),4));
plt.legend()
plt.title("Portfolio Value over time using Monte Carlo method (3b)")
plt.show()

#plotting the data for question 3c
plt.plot(date_list, best_port_value, label = "Highest Sharpe ratio")
plt.plot(date_list, worst_port_value, label = "Lowest risk portfolio")
plt.plot(date_list, safest_port_value, label = "Lowest Sharpe ratio")
plt.plot(date_list, equal_split_value, label = "Equal Split portfolio")
plt.xlabel("Date")
plt.ylabel("Value (dollars)")
plt.xticks(np.arange(0,len(date_list),40));
plt.legend()
plt.title("Portfolio Value over time using Sharpe ratio and risk (3c)")
plt.show()

#plotting the data for question 4
plt.plot(date_list, value_Random, color = "r", label = "Random")
plt.plot(date_list, value_SPY, color = "b", label = "SPY")
plt.plot(date_list, value_Regression, color = "y", label = "Linear Regression")
plt.plot(date_list, best_port_value, label = "Monte Carlo High Sharpe")
plt.plot(date_list, equal_split_value, label = "Equal Split portfolio")
plt.xlabel("Date")
plt.ylabel("Value (dollars)")
plt.xticks(np.arange(0,len(date_list),40));
plt.legend()
plt.title("Portfolio Worth over time using different investment strategies (Question 4)")
plt.show()

#plotting a value and price of AAPL over time
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
date_list2 = date_list [40:60]
price_history_apple = price_history_apple[40:60]
m_value_apple = m_value_apple [40:60]
ax1.plot(date_list2, price_history_apple, 'g-', label = "Price of AAPL")
ax1.set_ylim(min(price_history_apple)-1, max(price_history_apple)+1)
ax2.plot(date_list2, m_value_apple, 'b-', label = "a value")
ax1.set_xlabel('Date')
ax1.set_ylabel('Value (dollars)', color='g')
plt.xticks(np.arange(0,len(date_list2),4));
ax2.set_ylabel('a', color='b')
fig.legend(loc='upper right', bbox_to_anchor=(0.4, 0.85))
plt.title("Price and a value of AAPL over time (Question 2)")
plt.show()

#determining the time taken
end = time.perf_counter()
print(end-start)
    


import numpy as np 
import pandas as pd 
import requests 
import xlsxwriter 
import math 
from scipy import stats

stocks = pd.read_csv('sp500_stocks.csv')
# testing if program is importing stocks properly and API calls are working

# print(stocks)

#symbol = "IBM"
#api_url = 'https://sandbox.iexapis.com/stable/stock/{symbol}/stats?token={API_KEY}'
#data = requests.get(api_url).json()

#Function to split list into n-sized chunks sourced from
#https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks 
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

symbol_groups = list(chunks(stocks['Ticker'], 100))
symbol_strings = []
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))
#     print(symbol_strings[i])

my_columns = ['Ticker', 'Price', 'One-Year Price Return', 'Number of Shares to Buy']

final_dataframe = pd.DataFrame(columns = my_columns)

#next block of code will execute batch API call to get every ticker's price and one year price return
#number of shares to buy will be left blank for now 
for symbol_string in symbol_strings:
#     print(symbol_strings)
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=stats,quote&symbols={symbol_string}&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()
    for symbol in symbol_string.split(','):
        final_dataframe = final_dataframe.append(
            pd.Series([symbol, 
            data[symbol]['quote']['latestPrice'],
            data[symbol]['stats']['year1ChangePercent'],
            'N/A'
            ], 
            index = my_columns), 
            ignore_index = True)

# print(final_dataframe)

#sort values by highest one year price return
final_dataframe.sort_values('One-Year Price Return', ascending = False, inplace = True)
#grab top 50 stocks that fit our criteria
final_dataframe = final_dataframe[:51]
final_dataframe.reset_index(drop = True, inplace = True)

def portfolio_input():
    global portfolio_size
    portfolio_size = input("Enter the value of your portfolio:")

    try:
        val = float(portfolio_size)
    except ValueError:
        print("That's not a number! \n Try again:")
        portfolio_size = input("Enter the value of your portfolio:")

#take in portfolio value to calculate number of shares to buy
portfolio_input()
# print(portfolio_size)

#calculate number of shares to buy for each ticker
position_size = float(portfolio_size) / len(final_dataframe.index)
for i in range(0, len(final_dataframe['Ticker'])):
    final_dataframe.loc[i, 'Number of Shares to Buy'] = math.floor(position_size / final_dataframe['Price'][i])

#I stopped here and moved onto creating a more robust momentum trading bot


import numpy as np 
import pandas as pd 
import requests 
import xlsxwriter 
import math 
from scipy import stats
import yfinance as yf
import pandas_ta as ta

from API import get IEX_CLOUD_API_TOKEN
#in this bot, we are going to implement a more robust trading strategy whereby
#the bot uses more indicators and calculates a score to determine the quality of
#the momentum stock in question

#high quality in this case will be less volatile stocks that show consistent
#outperformance over the longterm whilst low quality stocks are ones that 
#have had a recent short burst in stock price 

#smoothed moving average calculator to get RSI
def smma(series,n):
    
    output=[series[0]]
    
    for i in range(1,len(series)):
        temp=output[-1]*(n-1)+series[i]
        output.append(temp/n)
        
    return output

def getRSI(df, period = 14):
    """ Returns a pd.Series with the relative strength index. """
    #calculate delta which is the difference between close prices
    close_delta = df['close'].diff()

    # Make two series: one for lower closes and one for higher closes
    up = close_delta.clip(lower=0)
    down = -1 * close_delta.clip(upper=0)
    
    #up=np.where(delta>0,delta,0)
    #down=np.where(delta<0,-delta,0)
    #is also valid


    # Use smoothed moving average that we calculated
    ma_up = smma(up, period)
    ma_down = smma(down, period)

    #relative strength calculation    
    rs = ma_up / ma_down
    rsi = 100 - (100/(1 + rs))
    return rsi

tickers = pd.read_csv('sp500_stocks.csv')

#Function to split list into n-sized chunks 
#https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks 
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

symbol_groups = list(chunks(tickers['Ticker'], 100))
symbol_strings = []
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))
#     print(symbol_strings[i])

my_columns = ['Ticker', 
            'Price', 
            'Number of Shares to Buy', 
            'One-Year Price Return', 
            'One-Year Return Percentile',
            'Six-Month Price Return',
            'Six-Month Return Percentile',
            'Three-Month Price Return',
            'Three-Month Return Percentile',
            'One-Month Price Return',
            'One-Month Return Percentile',
            'RSI',
            'HQM Score'
            ]

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
                                                   'N/A',
                                                   data[symbol]['stats']['year1ChangePercent'],
                                                   'N/A',
                                                   data[symbol]['stats']['month6ChangePercent'],
                                                   'N/A',
                                                   data[symbol]['stats']['month3ChangePercent'],
                                                   'N/A',
                                                   data[symbol]['stats']['month1ChangePercent'],
                                                   'N/A',
                                                   'N/A'
                                                   ], 
                                                  index = my_columns), 
                                        ignore_index = True)

# print(final_dataframe)


#now we calculate momentum percentiles for each stock in our dataframe
#more specifically, we calculate percentile scores for each stock in the following
#columns/metrics
time_periods = [
                'One-Year',
                'Six-Month',
                'Three-Month',
                'One-Month'
                ]

for row in final_dataframe.index:
    for time_period in time_periods:
       final_dataframe.loc[row, f'{time_period} Return Percentile'] = stats.percentileofscore(final_dataframe[f'{time_period} Price Return'], final_dataframe.loc[row, f'{time_period} Price Return'])/100

#Print each percentile score to make sure it was calculated properly
#for time_period in time_periods:
#    print(final_dataframe[f'{time_period} Return Percentile'])

from statistics import mean

for row in final_dataframe.index:
    momentum_percentiles = []
    for time_period in time_periods:
        momentum_percentiles.append(final_dataframe.loc[row, f'{time_period} Return Percentile'])
    final_dataframe.loc[row, 'HQM Score'] = mean(momentum_percentiles)

#sort values by HQM score which is our indicator of a good high quality 
#momentum stock

final_dataframe.sort_values('HQM Score', ascending = False, inplace = True)
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

#now we export our data to excel using xlsxWriter library

writer = pd.ExcelWriter('momentum_strategy.xlsx', engine='xlsxwriter')
final_dataframe.to_excel(writer, sheet_name='Momentum Strategy', index = False)

#below is the formatting for the excel file
background_color = '#0a0a23'
font_color = '#ffffff'

string_template = writer.book.add_format(
        {
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

dollar_template = writer.book.add_format(
        {
            'num_format':'$0.00',
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

integer_template = writer.book.add_format(
        {
            'num_format':'0',
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

percent_template = writer.book.add_format(
        {
            'num_format':'0.0%',
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

column_formats = { 
                    'A': ['Ticker', string_template],
                    'B': ['Price', dollar_template],
                    'C': ['Number of Shares to Buy', integer_template],
                    'D': ['One-Year Price Return', percent_template],
                    'E': ['One-Year Return Percentile', percent_template],
                    'F': ['Six-Month Price Return', percent_template],
                    'G': ['Six-Month Return Percentile', percent_template],
                    'H': ['Three-Month Price Return', percent_template],
                    'I': ['Three-Month Return Percentile', percent_template],
                    'J': ['One-Month Price Return', percent_template],
                    'K': ['One-Month Return Percentile', percent_template],
                    'L': ['HQM Score', integer_template]
                    }

for column in column_formats.keys():
    writer.sheets['Momentum Strategy'].set_column(f'{column}:{column}', 20, column_formats[column][1])
    writer.sheets['Momentum Strategy'].write(f'{column}1', column_formats[column][0], string_template)

writer.save()

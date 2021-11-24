import pandas as pd
import yfinance
from yahoo_fin import stock_info as si

def findTickers():
    dow = pd.DataFrame(si.tickers_dow())
    sp = pd.DataFrame(si.tickers_sp500())
    nasdaq = pd.DataFrame(si.tickers_nasdaq())
    others = pd.DataFrame(si.tickers_other())

    # convert DataFrame to list, then to sets
    sym1 = set( symbol for symbol in dow[0].values.tolist() )
    sym2 = set( symbol for symbol in sp[0].values.tolist() )
    sym3 = set( symbol for symbol in nasdaq[0].values.tolist() )
    sym4 = set( symbol for symbol in others[0].values.tolist() )

    tickers = set.union(sym1,sym2,sym3,sym4)

    # Some stocks are 5 characters. Those stocks with the suffixes listed below are not of interest.
    badChars = ['W', 'R', 'P', 'Q']
    goodTickers = set()

    for ticker in tickers:
        if len(ticker) > 4 and ticker[-1] in badChars:
            print("{ticker} is deliquent")
        else:
            goodTickers.add(ticker)
    return goodTickers

def findGoodStocks(tickers):
    goodTickers = []
    

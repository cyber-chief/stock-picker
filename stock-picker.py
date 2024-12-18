import pandas as pd
import yfinance as yf
from yahoo_fin import stock_info as si
import datetime
from dateutil.relativedelta import relativedelta
from flask import Flask, render_template, request
from GoogleNews import GoogleNews

app = Flask(__name__)


def getEPSResults(stock):
    incomeStmt = stock.income_stmt
    print(stock)
    print(incomeStmt)
    epsYoY = incomeStmt.iloc[20]
    epsYoY = epsYoY.values
    return epsYoY

def getFreeCash(stock):
    freeCash = stock.cash_flow.iloc[0]
    freeCash = freeCash.values
    return freeCash

def getSales(stock):
    revenue = stock.income_stmt.iloc[41]
    revenue = revenue.values
    return revenue

def getEquity(stock):
    equity = stock.balance_sheet.iloc[12]
    equity = equity.values

    return equity

def getROIC(stock):
    ebit = stock.income_stmt.iloc[9].values
    taxRate = stock.income_stmt.iloc[1].values
    investedCap = stock.balance_sheet.iloc[6].values

    roic = []

    for e,t,i in zip(ebit, taxRate, investedCap):
        n = e *(1-t)
        r = n/i * 100
        roic.append(r)

    return roic

def getSticker(eps, growthRate, futurePE, returnRate, years):
    futureEPS = eps
    growthRate = 1 + growthRate
    for i in range(years):
        futureEPS = futureEPS * growthRate

    futurePrice = futureEPS * futurePE
    stickerPrice = futurePrice/4
    margin = stickerPrice/2

    return margin


def getGrowth(values):
    rates = []
    for i in range(len(values)-1):
        rate = values[i]/values[i+1]
        rate = rate - 1
        rate = rate * 100
        rates.append(rate)
    return rates

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
    goodTickers = []
    #need to figure out how to remove index funds and others from this list
    for ticker in tickers:
        ticker =str(ticker)
        if (not len(ticker) > 4) or (ticker[-1:] in badChars):
            goodTickers.append(ticker)
    return goodTickers

def findGoodStocks(tickers):
    goodTickers = []
    currentDate = datetime.datetime.now()
    print(len(tickers))
    stock = yf.Ticker(tickers[120])
    eps = getEPSResults(stock)
    epsGrowth = getGrowth(eps)
    freeCash = getFreeCash(stock)
    cashGrowth = getGrowth(freeCash)
    revenue = getSales(stock)
    revenueGrowth = getGrowth(revenue)
    equity = getEquity(stock)
    equityGrowth = getGrowth(equity)
    roicRate = getROIC(stock)

stocks = findTickers()
findGoodStocks(stocks)

#landing page
@app.route('/', methods=['GET'])
def getHome():
    return render_template('home.html')

#render stock data for selected stock
@app.route("/stockInfo", methods=['POST'])
def getStock():
    ticker = request.form.get('stock')
    stock = yf.Ticker(ticker)
    peRatio = stock.info.get("forwardPE")
    priceSale = stock.info.get("priceToSalesTrailing12Months")
    priceBook = stock.info.get("priceToBook")
    eps = getEPSResults(stock)
    epsGrowth = getGrowth(eps)
    freeCash = getFreeCash(stock)
    cashGrowth = getGrowth(freeCash)
    revenue = getSales(stock)
    revenueGrowth = getGrowth(revenue)
    equity = getEquity(stock)
    equityGrowth = getGrowth(equity)
    roicRate = getROIC(stock)
    marginPrice = getSticker(6.59,0.07,20,15,10)
    print(marginPrice)
    return render_template('stockInfo.html', ticker=ticker, pe_ratio=peRatio, ps_ratio=priceSale, pb_ratio=priceBook)


#return already evaluated stocks on Rule 1 metrics
@app.route('/goodStocks', methods=['GET'])
def goodStocks():
    return render_template('goodStocks.html')

if __name__ == '__main__':
    app.run(debug=True)
import pandas as pd
import yfinance as yf
from yahoo_fin import stock_info as si
import datetime
from dateutil.relativedelta import relativedelta
from flask import Flask, render_template, request
from GoogleNews import GoogleNews


app = Flask(__name__)


def getEPSResults(stock):

    try:
        incomeStmt = stock.income_stmt
        eps = incomeStmt.loc['Basic EPS']
        eps = eps.values
    except: 
        eps = [0,0,0]
    return eps

def getFreeCash(stock):
    try:
        freeCash = stock.cash_flow.loc['Free Cash Flow']
        freeCash = freeCash.values
    except:
        freeCash = [0,0,0]
    return freeCash

def getSales(stock):
    try:
        revenue = stock.income_stmt.loc['Total Revenue']
        revenue = revenue.values
    except:
        revenue = [0,0,0]
    return revenue

def getEquity(stock):
    try:
        equity = stock.balance_sheet.loc['Stockholders Equity']
        equity = equity.values
    except:
        equit = [0,0,0]
    return equity

def getROIC(stock):

    incomeStmt = stock.income_stmt
    balanceSheet = stock.balance_sheet
    try:
        ebit = incomeStmt.loc['EBIT']
        taxRate = incomeStmt.loc['Tax Rate For Calcs']
        investedCap = balanceSheet.loc['Invested Capital']
    except:
        ebit = [0,0,0]
        taxRate = [0,0,0]
        investedCap = [0,0,0]

    roic = []

    for e,t,i in zip(ebit, taxRate, investedCap):
        if i == 0:
            roic.append(0)
        else:
            n = e *(1-t)
            r = n/i * 100
            roic.append(round(r, 2))

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
        if values[i+1] == 0:
            return [0,0,0]
        rate = values[i]/values[i+1]
        if values[i] <0 and values[i+1] <0:
            rate = (rate -1) * -1
        else:
            rate = rate - 1
        rate = rate * 100
        rates.append(round(rate, 2))
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
        if ( len(ticker) <= 4) or (ticker[-1:] in badChars):
            goodTickers.append(ticker)
    return goodTickers

def isGoodRate(rates):
    for rate in rates:
        if rate < 10:
            return False

    return True

def findGoodStocks(tickers):
    goodTickers = []
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        eps = getEPSResults(stock)
        epsGrowth = getGrowth(eps)
        if isGoodRate(epsGrowth):
            freeCash = getFreeCash(stock)
            cashGrowth = getGrowth(freeCash)
            if isGoodRate(cashGrowth):
                revenue = getSales(stock)
                revenueGrowth = getGrowth(revenue)
                if isGoodRate(revenueGrowth):
                    equity = getEquity(stock)
                    equityGrowth = getGrowth(equity)
                    if isGoodRate(equityGrowth):
                        roicRate = getROIC(stock)
                        if isGoodRate(roicRate):
                            goodTickers.append(ticker)
                            print(ticker +" has good financials")
    print(goodTickers)
    

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

    return render_template('stockInfo.html', ticker=ticker, pe_ratio=peRatio, ps_ratio=priceSale, pb_ratio=priceBook, eps_growth=epsGrowth, equity_growth=equityGrowth, fcf_growth=cashGrowth, revenue_growth=revenueGrowth, roic=roicRate)


#return already evaluated stocks on Rule 1 metrics
@app.route('/goodStocks', methods=['GET'])
def goodStocks():
    return render_template('goodStocks.html')

@app.route('/stickerPrice', methods=['GET','POST'])
def stickerPage():
    stickerPrice = None
    if request.method == "POST":
        try:
            # Retrieve form inputs
            eps = float(request.form["eps"])  # Earnings Per Share
            future_pe = float(request.form["future_pe"])  # Future Price-to-Earnings Ratio
            growth_rate = float(request.form["growth_rate"]) / 100  # Convert Growth Rate (%) to decimal
            return_rate = float(request.form["return_rate"]) / 100  # Convert Return Rate (%) to decimal
            years = int(request.form["years"])  # Number of Years
            stickerPrice = getSticker(eps, growth_rate, future_pe, return_rate, years)
        except (ValueError, KeyError) as e:
            # Handle invalid or missing inputs gracefully
            sticker_price = "Invalid Input"

    return render_template('stickerPrice.html', sticker_price=stickerPrice)


if __name__ == '__main__':
    app.run(debug=True)
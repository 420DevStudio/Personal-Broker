import tkinter as tk
from tkinter import ttk
import time

import bs4 as bs
import pickle
import requests

import datetime as dt
import pandas as pd
from pandas import DataFrame
from pandas_datareader import data as pdr
import yfinance as yf

import os

import logging
from pathlib import Path

LARGE_FONT = ('Verdana', 12)

startyear = 2015
startmonth = 1
startday = 1
start = dt.datetime(startyear, startmonth, startday)

# endyear = 2020
# endmonth = 2
# endday = 1
# end = dt.datetime(endyear, endmonth, endday)

end = dt.datetime.now()

HISTORICAL_DATA_PATH = Path("Data/HistoricalData")
DAYS_PER_WEEK = 5

LOG = logging.getLogger(__name__)

class Disclaimer(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)

        label = tk.Label(self, text="""
        
         - Personal Broker Haftungsausschluss -

        Bei dieser Anwendung handelt es sich um eine 'alpha-version' zu testzwecken.
        Sie sollte nicht als Anlagetool oder Ratgeber verwendet werden.
        Der Autor der Anwendung übernimmt ausdrücklich keinerlei Gewährleistung in
        Bezug auf Funktionalität und/oder Korrektheit der Ergebnisse.
        Mit klicken auf 'Zustimmen' erklären Sie sich mit diesen Bedingungen einverstanden.
        Ein Klick auf 'Ablehnen' beendet die Anwendung.
        
        """, font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = ttk.Button(self, text='Zustimmen', command=lambda: controller.show_frame(HomePage))
        button1.pack()

        button2 = ttk.Button(self, text='Ablehnen', command=quit)
        button2.pack()

class HomePage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        mainCanvas = tk.Canvas(self, bg='black')
        mainCanvas.grid(column=0, row=0, columnspan=2, sticky='nsew')

        navigationCanvas = tk.Canvas(self, bg='blue')
        navigationCanvas.grid_columnconfigure(0, weight=1)
        navigationCanvas.grid_rowconfigure((0,1,2,3), weight=1)
        navigationCanvas.grid(column=0, row=0, padx=5, pady=5, sticky='NSEW')

        btn_MyPortfolio = ttk.Button(navigationCanvas, text='Mein Portfolio',
                                                command=lambda: controller.show_frame(MyPortfolio))
        btn_MyPortfolio.grid(column=0, row=0, padx=5, pady=5, sticky='NESW')

        btn_FindStocks = ttk.Button(navigationCanvas, text='Aktien Finder', command=lambda: controller.show_frame(StockFinder))
        btn_FindStocks.grid(column=0, row=1, padx=5, pady=5, sticky='NESW')

        btn_HomePage = ttk.Button(navigationCanvas, text='Home Page', command=lambda: controller.show_frame(Disclaimer))
        btn_HomePage.state(['disabled'])
        btn_HomePage.grid(column=0, row=3, padx=5, pady=5, sticky='NESW')

        button4 = ttk.Button(navigationCanvas, text='Beenden', command=quit)
        button4.grid(column=0, row=4, padx=5, pady=5, sticky='NESW')

        userViewCanvas = tk.Canvas(self, bg='blue')
        userViewCanvas.grid_columnconfigure((0,1,2,3), weight=1)        
        userViewCanvas.grid_rowconfigure((0,1,2,3), weight=1)
        
        lbl_PageTitle = tk.Label(userViewCanvas, text='Personal Broker - Home', anchor='center', font=LARGE_FONT)
        lbl_PageTitle.grid(column=0, row=0, columnspan=4, rowspan=1, padx=5, pady=5, sticky='NESW')
        userViewCanvas.grid(column=1, row=0, columnspan=7, padx=5, pady=5, sticky='NSEW')

class MyPortfolio(tk.Frame):

    def save_Dax_Tickers(self, parent, controller, lbl_PortfolioOverview):

        response = requests.get('https://de.wikipedia.org/wiki/DAX')
        soup = bs.BeautifulSoup(response.text, 'lxml')
        table = soup.find('table', {'class': 'wikitable sortable'})

        tickers = []
        for row in table.find_all('tr')[1:]:
            ticker = row.find_all('td')[1].text
            if '.' in ticker:
                ticker = ticker.replace('.','-')
            tickers.append(ticker + '.DE')

        with open('Data/tickers/DAX_tickers.pickle', 'wb') as f:
            pickle.dump(tickers, f)

        return tickers

    def save_sp500_tickers(self, parent, controller, lbl_PortfolioOverview):

        resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
        soup = bs.BeautifulSoup(resp.text, 'lxml')
        table = soup.find('table', {'class': 'wikitable sortable'})

        tickers = []
        for row in table.find_all('tr')[1:]:
            ticker = row.find_all('td')[0].text
            if '.' in ticker:
                ticker = ticker.replace('.','-')
            ticker = ticker[:-1]
            tickers.append(ticker)

        with open('Data/tickers/sp500tickers.pickle', 'wb') as f:
            pickle.dump(tickers, f)

        return tickers

    def createPortfolio(self, parent, controller, lbl_PortfolioOverview):

        # read in dax tickers and create stocklist

        try:
            Dax_list_pickle = pd.read_pickle('Data/tickers/DAX_tickers.pickle')
            stocklist = DataFrame(Dax_list_pickle, columns=['tickers'])
            exportlist = pd.DataFrame(columns=['Stock', 'RS_Rating', '50 Day MA', '150 Day MA', '200 Day MA', '52 Week Low', '52 Week High'])

            # print(type(stocklist))
            # print(stocklist)
            # print(type(exportlist))
            # print(exportlist)
        except Exception:
            
            MyPortfolio(parent, controller).save_Dax_Tickers(parent, controller)

            Dax_list_pickle = pd.read_pickle('Data/tickers/DAX_tickers.pickle')
            stocklist = DataFrame(Dax_list_pickle, columns=['tickers'])
            exportlist = pd.DataFrame(columns=['Stock', 'RS_Rating', '50 Day MA', '150 Day MA', '200 Day MA', '52 Week Low', '52 Week High'])

        # read in s&p500 tickers and create stocklist_sp500
        
        try:
            sp500_list_pickle = pd.read_pickle('Data/tickers/sp500tickers.pickle')
            stocklist_sp500 = DataFrame(sp500_list_pickle, columns=['tickers'])
        except Exception:
            MyPortfolio(parent, controller).save_sp500_tickers(parent, controller)

            sp500_list_pickle = pd.read_pickle('Data/tickers/sp500tickers.pickle')
            stocklist_sp500 = DataFrame(Dax_list_pickle, columns=['tickers'])

        stocklist_complete = stocklist.append(stocklist_sp500, ignore_index=True, sort=False)
        # print(stocklist_complete)
        
        # Kalkulation des Relative Stärke Index (RSI) von:
        # https://www.learnpythonwithrune.org/pandas-calculate-the-relative-strength-index-rsi-on-a-stock/

        for i in stocklist.index:
            stock = str(stocklist['tickers'][i])

            try:
                df_RS_Rating = pdr.get_data_yahoo(stock, start, end)
                df_RS_Rating.drop(['Open', 'High', 'Low', 'Close', 'Volume'], 1, inplace=True)
                df_RS_Rating['Diff Vortag'] = df_RS_Rating.diff()
                
                delta = df_RS_Rating['Adj Close'].diff()
                up = delta.clip(lower=0)
                down = -1*delta.clip(upper=0)
                ema_up = up.ewm(com=13, adjust=False).mean()
                ema_down = down.ewm(com=13, adjust=False).mean()
                rs = ema_up/ema_down

                df_RS_Rating['RSI'] = 100 - (100/(1 + rs))

                # Skip first 14 days to have real values
                df_RS_Rating = df_RS_Rating.iloc[14:]

                # print(df_RS_Rating.head())
            except Exception:
                print('sth. went wrong')
                print(Exception.with_traceback())

        # Auswahl der Aktien aus dem DAX, welche Mark Minervinis Trend Template Kriterien erfüllen.
        # siehe auch: https://www.youtube.com/watch?v=hngHA9Jjbjc&list=PLPfme2mwsQ1FQhH1icKEfiYdLSUHE-Wo5&index=3

        for i in stocklist.index:
            stock = str(stocklist['tickers'][i])
            RS_Rating = df_RS_Rating['RSI'][i]

            try:
                df = pdr.get_data_yahoo(stock, start, end)
                # print(df.head())                
                
                smaUsed = [50, 150, 200]

                for x in smaUsed:
                    sma = x
                    df['SMA_' + str(sma)] = round(df.iloc[:,5].rolling(window=sma).mean(), 2)
                
                currentClose = df['Adj Close'][-1]
                moving_average_50 = df['SMA_50'][-1]
                moving_average_150 = df['SMA_150'][-1]
                moving_average_200 = df['SMA_200'][-1]

                low_of_52week = min(df['Adj Close'][-260:])
                high_of_52week = max(df['Adj Close'][-260:])
                
                try:
                    moving_average_200_20past = df['SMA_200'][-20]
                except Exception:
                    moving_average_200_20past = 0

                print('Checking ' + stock + ' ...')

                # Condition 1: Current price > 150 SMA and > 200 SMA
                if (currentClose > moving_average_150 and currentClose > moving_average_200):
                    cond_1 = True
                    # print(currentClose)
                    # print(moving_average_150)
                    # print(moving_average_200)
                    # print('cond_1 is True')
                else:
                    cond_1 = False
                    # print(currentClose)
                    # print(moving_average_150)
                    # print(moving_average_200)
                    # print('cond_1 is False')

                # Condition 2: 150 SMA > 200 SMA
                if (moving_average_150 > moving_average_200):
                    cond_2 = True
                    # print('cond_2 is True')
                else:
                    cond_2 = False
                    # print('cond_2 is False')

                # Condition3: 200 SMA trending up for at least 1 month (ideally 4-5 months)
                if (moving_average_200 > moving_average_200_20past):
                    cond_3 = True
                    # print('cond_3 is True')
                else:
                    cond_3 = False
                    # print('cond_3 is False')

                # Condition 4: 50 SMA > 150 SMA and 50 SMA > 200 SMA
                if (moving_average_50 > moving_average_150 and moving_average_50 > moving_average_200):
                    cond_4 = True
                    # print('cond_4 is True')
                else:
                    cond_4 = False
                    # print('cond_4 is False')

                # Condition 5: Current price > 50 SMA
                if (currentClose > moving_average_50):
                    cond_5 = True
                    # print('cond_5 is True')
                else:
                    cond_5 = False
                    # print('cond_5 is False')

                # Condition 6: Current price is at least 30% above 52 weeks low (many of the best are up to 100 - 300% above)
                if (currentClose >= (1.3*low_of_52week)):
                    cond_6 = True
                    # print('cond_6 is True')
                else:
                    cond_6 = False
                    # print('cond_6 is False')

                # Condition 7: Current price is within 25% of 52 week high
                if (currentClose >= (.75*high_of_52week)):
                    cond_7 = True
                    # print('cond_7 is True')
                else:
                    cond_7 = False
                    # print('cond_7 is False')

                # Condition 8: (IBD) RS rating > 70 and the higher the better
                if (RS_Rating > 70):
                    cond_8 = True
                    # print('cond_8 is True')
                else:
                    cond_8 = False
                    # print('cond_8 is False')

                if(cond_1 and cond_2 and cond_3 and cond_4 and cond_5 and cond_6 and cond_7 and cond_8):
                    exportlist = exportlist.append({'Stock': stock, 'RS_Rating': RS_Rating, '50 Day MA': moving_average_50, '150 Day MA': moving_average_150, '200 Day MA': moving_average_200, '52 Week Low': low_of_52week, '52 Week High': high_of_52week}, ignore_index=True)

            except Exception:
                print('No Data on ' + stock)
                print(Exception.with_traceback())

        print(exportlist)

        self.lbl_PortfolioOverview.configure(text = exportlist)

    def createPortfolioLocal(self, parent, controller, lbl_PortfolioOverview):

        starttime = time.time()
        path = 'Data/HistoricalData'
        exportlist = pd.DataFrame(columns=['Stock', 'RS_Rating', '50 Day MA', '150 Day MA', '200 Day MA', '52 Week Low', '52 Week High'])
        exportlist = list()
        
        for filename in os.listdir(path):

            try:
                df_rs_rating = pd.read_csv(os.path.join(path, filename))
                df_rs_rating = pd.DataFrame(df_rs_rating)
                df_rs_rating['Diff Vortag'] = df_rs_rating['Adj Close'].diff()
                delta = df_rs_rating['Adj Close'].diff()
                up = delta.clip(lower=0)
                down = -1*delta.clip(upper=0)
                ema_up = up.ewm(com=13, adjust=False).mean()
                ema_down = down.ewm(com=13, adjust=False).mean()
                rs = ema_up/ema_down
                df_rs_rating['RSI'] = 100 - (100/(1 + rs))
                
                df_rs_rating['ticker'] = filename[:-4]
                stock = df_rs_rating['ticker']
                RS_Rating = df_rs_rating['RSI']
                df_rs_rating.reset_index(inplace=False)
                df_rs_rating.set_index('Date', inplace=True)

                # Skip first 14 days to have real values
                df_rs_rating = df_rs_rating.iloc[14:]
            except Exception:
                print('sth. went wrong')
                print(Exception.with_traceback())

            try:

                smaUsed = [50, 150, 200]

                for x in smaUsed:
                    df_rs_rating['SMA_' + str(x)] = round(df_rs_rating.iloc[:,5].rolling(window=x).mean(), 2)
                            
                current_close = df_rs_rating['Adj Close'][-1]
                moving_average_50 = df_rs_rating['SMA_50'][-1]
                moving_average_150 = df_rs_rating['SMA_150'][-1]
                moving_average_200 = df_rs_rating['SMA_200'][-1]

                low_of_52week = min(df_rs_rating['Adj Close'][-260:])
                high_of_52week = max(df_rs_rating['Adj Close'][-260:])
                    
                try:
                    moving_average_200_20past = df_rs_rating['SMA_200'][-20]
                except Exception:
                    moving_average_200_20past = 0

                print('Checking ' + filename + ' ...')
                print(df_rs_rating.tail())

                conditions = [
                    current_close > max(moving_average_150, moving_average_200),
                    moving_average_150 > moving_average_200,
                    moving_average_200 > moving_average_200_20past,
                    moving_average_50
                    > max(moving_average_150, moving_average_200),
                    current_close > moving_average_50,
                    current_close >= 1.3 * low_of_52week,
                    current_close >= 0.75 * high_of_52week,
                    # rs_rating >= 70 - if uncommented -> The truth value of a Series is ambiguous. Use a.empty, a.bool(), a.item(), a.any() or a.all().
                ]
            
                if all(conditions):
                    exportlist.append(
                        pd.DataFrame(
                            {
                                "Stock": stock,
                                "RS_Rating": RS_Rating,
                                "50 Day MA": moving_average_50,
                                "150 Day MA": moving_average_150,
                                "200 Day MA": moving_average_200,
                                "52 Week Low": low_of_52week,
                                "52 Week High": high_of_52week,
                            }
                        )
                        
                    )

            except Exception:
                print('No Data on ' + stock)
                print(Exception.with_traceback())

        df = pd.DataFrame(exportlist)
        print(df.head())
        df.to_csv('exportlist.csv')

        print(len(exportlist))
        self.lbl_PortfolioOverview.configure(text = exportlist)
        endtime = time.time()
        print(endtime - starttime)

    def create_portfolio_from_local_files(self, parent, controller, lbl_PortfolioOverview):

        start_time = time.monotonic()

        stock_dataframes = list()
        for file_path in HISTORICAL_DATA_PATH.iterdir():
            stock = file_path.stem
            try:
                df_rs_rating = pd.read_csv(file_path)

                delta = df_rs_rating["Adj Close"].diff()
                df_rs_rating["Diff Vortag"] = delta

                ema_up = delta.clip(lower=0).ewm(com=13, adjust=False).mean()
                ema_down = (-delta.clip(upper=0)).ewm(com=13, adjust=False).mean()
                rs_rating = 100 * ema_up / (ema_up + ema_down)
                df_rs_rating["RSI"] = rs_rating

                df_rs_rating["ticker"] = stock

                df_rs_rating.set_index("Date", inplace=True)
                #
                # Skip first 14 days to have real values.
                #
                df_rs_rating = df_rs_rating.iloc[14:]

                for window_size in [50, 150, 200]:
                    #
                    # TODO Use column name instead of the magical 5 as column index.
                    #
                    df_rs_rating[f"SMA_{window_size}"] = (
                        df_rs_rating.iloc[:, 5]
                        .rolling(window=window_size)
                        .mean()
                        .round(2)
                    )

                current_close = df_rs_rating["Adj Close"][-1]
                moving_average_50 = df_rs_rating["SMA_50"][-1]
                moving_average_150 = df_rs_rating["SMA_150"][-1]
                moving_average_200 = df_rs_rating["SMA_200"][-1]

                # low_of_52week, high_of_52week = df_rs_rating["Adj Close"][
                #     -52 * DAYS_PER_WEEK
                # ].agg(["min", "max"])

                low_of_52week = min(df_rs_rating['Adj Close'][-260:])
                high_of_52week = max(df_rs_rating['Adj Close'][-260:])

                moving_average_200_20past = df_rs_rating["SMA_200"].get(-20, 0)

                print("Checking", file_path.name, "...")
                print(df_rs_rating.tail())

                conditions = [
                    current_close > max(moving_average_150, moving_average_200),
                    moving_average_150 > moving_average_200,
                    moving_average_200 > moving_average_200_20past,
                    moving_average_50
                    > max(moving_average_150, moving_average_200),
                    current_close > moving_average_50,
                    current_close >= 1.3 * low_of_52week,
                    current_close >= 0.75 * high_of_52week,
                    # rs_rating >= 70 - if uncommented -> The truth value of a Series is ambiguous. Use a.empty, a.bool(), a.item(), a.any() or a.all().
                ]
                if all(conditions):
                    stock_dataframes.append(
                        pd.DataFrame(
                            {
                                "Stock": stock,
                                "RS_Rating": rs_rating,
                                "50 Day MA": moving_average_50,
                                "150 Day MA": moving_average_150,
                                "200 Day MA": moving_average_200,
                                "52 Week Low": low_of_52week,
                                "52 Week High": high_of_52week,
                            }
                        )
                    )

            except Exception:
                LOG.exception("No data on %s", stock)

        result = pd.concat(stock_dataframes, ignore_index=True)
        result.to_csv("exportlist.csv")
        print(result.head())
        print(len(result))
        print(time.monotonic() - start_time)
        return result
                

    def getMyPortfolio(self, lbl_PortfolioOverview):

        try:
            # print(self.lbl_PortfolioOverview.configure(text = 'endlich richtig'))
            self.lbl_PortfolioOverview.configure(text = 'endlich richtig')
            print('endlich richtig')
        except Exception:
            print('\n' + 'schon wieder falsch...' + '\n')
            print(Exception.with_traceback())

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        self.mainCanvas = tk.Canvas(self, bg='black')
        self.mainCanvas.grid(column=0, row=0, columnspan=2, sticky='nsew')

        self.navigationCanvas = tk.Canvas(self, bg='blue')
        self.navigationCanvas.grid_columnconfigure(0, weight=1)
        self.navigationCanvas.grid_rowconfigure((0,1,2,3), weight=1)
        self.navigationCanvas.grid(column=0, row=0, padx=5, pady=5, sticky='NSEW')

        self.btn_CheckPortfolio = ttk.Button(self.navigationCanvas, text='Check Portfolio',
                                                command=lambda: MyPortfolio.getMyPortfolio(self, self.lbl_PortfolioOverview))
        self.btn_CheckPortfolio.grid(column=0, row=0, padx=5, pady=5, sticky='NESW')

        self.btn_CreatePortfolio = ttk.Button(self.navigationCanvas, text='Portfolio erstellen', 
                                                command=lambda: MyPortfolio.createPortfolioLocal(self, parent, controller, self.lbl_PortfolioOverview))
        self.btn_CreatePortfolio.grid(column=0, row=1, padx=5, pady=5, sticky='NESW')

        self.btn_HomePage = ttk.Button(self.navigationCanvas, text='Home Page',
                                                command=lambda: controller.show_frame(HomePage))
        self.btn_HomePage.grid(column=0, row=3, padx=5, pady=5, sticky='NESW')

        self.btn_Quit = ttk.Button(self.navigationCanvas, text='Beenden', 
                                                command=quit)
        self.btn_Quit.grid(column=0, row=4, padx=5, pady=5, sticky='NESW')

        self.userViewCanvas = tk.Canvas(self, bg='blue')
        self.userViewCanvas.grid_columnconfigure((0,1,2,3), weight=1)        
        self.userViewCanvas.grid_rowconfigure((0,1,2,3), weight=1)        

        self.lbl_PageTitle = tk.Label(self.userViewCanvas, text='Personal Broker - Mein Portfolio', anchor='center', font=LARGE_FONT)
        self.lbl_PageTitle.grid(column=0, row=0, columnspan=4, rowspan=1, padx=5, pady=5, sticky='NESW')
        self.lbl_PortfolioOverview = tk.Label(self.userViewCanvas, text='Dummy Text', anchor='center', font=LARGE_FONT)
        self.lbl_PortfolioOverview.grid(column=0, row=1, columnspan=4, rowspan=2, padx=5, pady=5, sticky='NESW')
        self.userViewCanvas.grid(column=1, row=0, columnspan=7, padx=5, pady=5, sticky='NSEW')

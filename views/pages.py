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

endyear = 2021
endmonth = 2
endday = 24
end = dt.datetime(endyear, endmonth, endday)

# end = dt.datetime.now()

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

    def create_portfolio_from_local_files(self, parent, controller, lbl_PortfolioOverview):

        start_time = time.monotonic()
        counter = 0
        stock_dataframes = list()

        for file_path in HISTORICAL_DATA_PATH.iterdir():
            stock = file_path.stem
            counter += 1
            try:
                df_rs_rating = pd.read_csv(file_path)
                date = df_rs_rating["Date"]

                delta = df_rs_rating["Adj Close"].diff()
                df_rs_rating["Diff Vortag"] = delta

                ema_up = delta.clip(lower=0).ewm(com=13, adjust=False).mean()
                ema_down = (-delta.clip(upper=0)).ewm(com=13, adjust=False).mean()
                rs_rating = 100 * ema_up / (ema_up + ema_down)
                df_rs_rating["RSI"] = rs_rating

                df_rs_rating["ticker"] = stock

                df_rs_rating.set_index("Date", inplace=True)
                
                # Skip first 14 days to have real values.
                df_rs_rating = df_rs_rating.iloc[14:]

                for window_size in [50, 150, 200]:
                    df_rs_rating[f"SMA_{window_size}"] = (
                        df_rs_rating["Adj Close"]
                        .rolling(window=window_size)
                        .mean()
                        .round(2)
                    )

                current_close = df_rs_rating["Adj Close"][-1]
                moving_average_50 = df_rs_rating["SMA_50"][-1]
                moving_average_150 = df_rs_rating["SMA_150"][-1]
                moving_average_200 = df_rs_rating["SMA_200"][-1]

                low_of_52week, high_of_52week = df_rs_rating["Adj Close"][
                    -52 * DAYS_PER_WEEK:
                ].agg(["min", "max"])

                moving_average_200_20past = df_rs_rating["SMA_200"].get(-20, 0)

                print("Checking", file_path.name, "...")

                conditions = [
                    current_close > max(moving_average_150, moving_average_200),
                    moving_average_150 > moving_average_200,
                    moving_average_200 > moving_average_200_20past,
                    moving_average_50
                    > max(moving_average_150, moving_average_200),
                    current_close > moving_average_50,
                    current_close >= 1.3 * low_of_52week,
                    current_close >= 0.75 * high_of_52week,
                ]
                if all(conditions):
                    stock_dataframes.append(
                        pd.DataFrame(
                            {
                                "Date": date,
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
        last_entrys = pd.DataFrame(result.loc[result['Date'] == '2021-02-24'])
        potential_portfolio = pd.DataFrame(last_entrys.loc[last_entrys['RS_Rating'] >= 80])
        potential_portfolio.reset_index(inplace=True, drop=True)
        potential_portfolio.to_csv('potential_portfolio.csv')
        percentage = (len(potential_portfolio)/counter) * 100
        print('\nHistorische Daten von ' + str(counter) + ' Unternehmen geprüft.')        
        print('\nDavon wurden ' + str(len(potential_portfolio)) + ' zur Erstellung eines Portfolios nach Mark Minervinis "Trend-Template" ausgewählt')
        print('\nDies entspricht einem Anteil von ' + str(round(percentage, 2)) + ' Prozent aller geprüften Unternehmen.\n')
        print(potential_portfolio.head(10))
        self.lbl_PortfolioOverview.configure(text = potential_portfolio.head(10))        
        print(time.monotonic() - start_time) 
                

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
                                                command=lambda: MyPortfolio.create_portfolio_from_local_files(self, parent, controller, self.lbl_PortfolioOverview))
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

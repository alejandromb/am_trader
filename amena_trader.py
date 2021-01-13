
import alpaca_trade_api as tradeapi
import time
import datetime
from datetime import timedelta
from pytz import timezone
tz = timezone('EST')
import matplotlib 

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd



#minute, 1Min, 5Min, 15Min, day or 1D. minute





import logging
logging.basicConfig(filename='./new_5min_ema.log', format='%(name)s - %(levelname)s - %(message)s')
logging.warning('{} logging started'.format(datetime.datetime.now().strftime("%x %X")))

class  amena_trader:

    def __init__(self):


        self.API_KEY = ""
        self.API_SECRET = ""
        self.APCA_API_BASE_URL ="https://paper-api.alpaca.markets"



        self.load_credentials()
        self.alpaca = tradeapi.REST(self.API_KEY, self.API_SECRET, self.APCA_API_BASE_URL, 'v2')
        self.symbols=['F']
        self.order_sleep_time=300


    def load_credentials(self ):
        cred_file = open('credentials.txt', 'r')
        
        file_contents = cred_file.read()
        Lines = file_contents.splitlines()

        

        self.API_KEY = Lines[0].split('=')[1]
        self.API_SECRET = Lines[1].split('=')[1]
        #self.APCA_API_BASE_URL = Lines[2].split('=')[1]

        print("apikey="+self.API_KEY)
        print("apisec="+self.API_SECRET)
        #print(self.APCA_API_BASE_URL)


    def get_data_bars(self,symbols, rate, slow, fast):
        data = self.alpaca.get_barset(symbols, rate, limit=20).df
        for x in symbols:
            data.loc[:, (x, 'fast_ema')] = data[x]['close'].rolling(window=fast).mean()
            data.loc[:, (x, 'slow_ema')] = data[x]['close'].rolling(window=slow).mean()
        return data

    def get_signal_bars(self,symbol_list, rate, ema_slow, ema_fast):
        data = self.alpaca.get_data_bars(symbol_list, rate, ema_slow, ema_fast)
        signals = {}
        for x in symbol_list:
            if data[x].iloc[-1]['fast_ema'] > data[x].iloc[-1]['slow_ema']: signal = 1
            else: signal = 0
            signals[x] = signal
        return signals

    def market_open(self):
        clock = self.alpaca.get_clock()
        #print('The market is {}'.format('open.' if clock.is_open else 'closed.'))
        if clock.is_open:
            print("open")
            return 1
        else:
            print("closed")
            return 0

    def get_data(self,rate):

        data = self.alpaca.get_barset(self.symbols, rate, limit=250).df

        return data


    def get_rolling_mean(self,data,window):
                
        """Return rolling mean of given values, using specified window size."""
        return data.rolling(window).mean()


    def get_rolling_std(self,data, window):
        """Return rolling standard deviation of given values, using specified window size."""
        # Compute and return rolling standard deviation
        return data.rolling(window).std()


    def time_to_open(self,current_time):
        if current_time.weekday() <= 4:
            d = (current_time + timedelta(days=1)).date()
        else:
            days_to_mon = 0 - current_time.weekday() + 7
            d = (current_time + timedelta(days=days_to_mon)).date()
        next_day = datetime.datetime.combine(d, datetime.time(9, 30, tzinfo=tz))
        seconds = (next_day - current_time).total_seconds()
        return seconds

    def bollingger_band(self,values):

        moving_average = self.get_rolling_mean(values,15) #df['close_price'].rolling(20).mean()
        std_deviation  = self.get_rolling_std(values,15)  #std_deviation = df['close_price'].rolling(20).std()

        upper_band=moving_average+std_deviation * 2
        lower_band = moving_average - std_deviation * 2

        return upper_band,lower_band

    def buy_stock(self,symb):
        try:
                
            self.alpaca.submit_order(

                symbol=symb,
                qty=1,
                side='buy',
                type='market',
                time_in_force='gtc'
            )
        except:
            print("error ocurred")
            

    def sell_stock(self,symb):
        try:


            self.alpaca.submit_order(

                symbol=symb,
                qty=1,
                side='sell',
                type='limit',
                time_in_force='opg',
                limit_price=self.last_trade_price(symb)*0.05
            )
        except:
            (" An exception occured on this line, captured error code...")


    def check_bollinger_signal(self,data,position):
             
        current_price=float(self.last_trade_price(self.symbols[0]))
        ub,lb=self.bollingger_band(data)

        upper_trigger=ub['close'][position]
        lower_trigger=lb['close'][position]


        
        if(current_price>=upper_trigger):

            print("buy_signal")
            self.buy_stock(self.symbols[0])
            return "buy"

        elif current_price<=lower_trigger:
            print("sell signal")
            self.sell_stock(self.symbols[0])
            return  "sell"
        else:
            print("no action")
            return "na"

       

    def last_trade_price(self,symbol):
        return self.alpaca.get_last_trade(symbol).price


    def crosssma(self,values,window_short,window_large):

        short_mean = values.rolling(window_short).mean()
        long_mean = values.rolling(window_large).mean()

        shifted_short = short_mean.shift(1)
        shifted_long = long_mean.shift(1)

        bearish_crossing = ((short_mean <= long_mean) & (shifted_short >= shifted_long))
        bullish_crossing = ((short_mean >= long_mean) & (shifted_short <= shifted_long))

        return bearish_crossing, bullish_crossing
        

  


    def run_backtrade_bollinger(self,values):

        #values2=trader.get_data('day',symbols2)
        ub,lb=trader.bollingger_band(values)
        vf=values['F'] 

        # for price in vf['close']
        values_close=vf['close']
        ub_close=ub['F']['close']
        lb_close=lb['F']['close']

        for i in range(len(vf)):

            if(values_close[i]>=ub_close[i]):

                print("buy_signal")
                plt.plot(i,values_close[i],'x')
                time.sleep(self.order_sleep_time)
                
            elif (values_close[i]<=lb_close[i]):

                plt.plot(i,values_close[i],'x')
                print("sell signal")     
                time.sleep(self.order_sleep_time)       
                
            else:
                print("no action")
                
            plt.plot(i,values_close[i],'*')
            plt.plot(i,ub_close[i],'.')
            plt.plot(i,lb_close[i],'.')



        plt.show()


    def run_paper_live(self):
        
        while True:
            if self.market_open():
                print('is open')
                data=self.get_data('5Min')
                stock=data[self.symbols[0]]
                self.check_bollinger_signal(stock,-1)

         
                
                time.sleep(60)
            else:
                clock = self.alpaca.get_clock()
                openingTime = clock.next_open.replace(tzinfo=datetime.timezone.utc).timestamp()
                currTime = clock.timestamp.replace(tzinfo=datetime.timezone.utc).timestamp()
                timeToOpen = int((openingTime - currTime) / 60)
                print(str(timeToOpen) + " minutes til market open.")
                time.sleep(60)    
                

        
                   





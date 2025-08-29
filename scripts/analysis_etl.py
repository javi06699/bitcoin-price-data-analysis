import pandas as pd
from sqlalchemy import create_engine
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import ListedColormap, BoundaryNorm
import matplotlib.dates as mdates
from prophet import Prophet
import os
import mplcursors



class FinancialDataAnalyzer:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        self.df = None
        self.monthly_return = None
        self.monthly_avg = None
    
#------------------------ETL------------------------
    def load_data(self, table='prices', start_date='2015-01-01'):
        
        query = f"SELECT * FROM {table};"
        self.df = pd.read_sql(query, self.engine).dropna()
        
        self.df['date'] = pd.to_datetime(self.df['date'])
         

        
        self.df = self.df[self.df['date'] >= start_date]
        self.df['year'] = self.df['date'].dt.year
        self.df['month'] = self.df['date'].dt.month
        self.df['year_month'] = self.df['date'].dt.to_period('M')
        
        return self.df

#------------------------ANALISIS------------------------   
    def calculate_monthly_return(self):
        monthly_prices = self.df.groupby(['asset_id', 'year_month'])['close'].agg(['first', 'last']).reset_index()
        
        monthly_prices['monthly_return'] = (monthly_prices['last'] - monthly_prices['first']) / monthly_prices['first']
        self.monthly_return = monthly_prices
        
        monthly_prices['month'] = monthly_prices['year_month'].dt.month
        self.monthly_avg = monthly_prices.groupby(['asset_id', 'month'])['monthly_return'].mean().reset_index()
    
    def get_asset_data(self, asset_id):
        return self.monthly_return[self.monthly_return['asset_id'] == asset_id], \
               self.monthly_avg[self.monthly_avg['asset_id'] == asset_id]

    def realized_price(self, asset_id,asset_label):
        df_asset = self.df[self.df['asset_id'] == asset_id]
        df_asset['vol_price'] = df_asset['close'] * df_asset['volume']
        df_asset['total_volume'] = df_asset['volume'].cumsum()
        df_asset['total_value'] = df_asset['vol_price'].cumsum()
        df_asset['realized_price'] = df_asset['total_value'] / df_asset['total_volume']
        fig,ax =plt.subplots(figsize=(12,6))
        RP, =ax.plot(df_asset['date'], df_asset['realized_price'], label='Realized price', color='orange')
        close_price=ax.plot(df_asset['date'], df_asset['close'], label='Close price', color='blue')
        ax.set_yscale('log')
        ax.get_yaxis().set_major_formatter(plt.ScalarFormatter())
        ax.ticklabel_format(axis='y', style='plain')
        ax.grid(which='both',linestyle='--',linewidth=0.5)
        mplcursors.cursor(RP,hover=True)
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.title(f'Realized price vs Close price for {asset_label}')
        plt.legend()
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
        plt.xticks(rotation=45)

        plt.show()

    def Short_realized_price(self, asset_id,asset_label):
        df_asset=self.df[self.df['asset_id']==asset_id]
        df_asset['vol_price']=df_asset['close']*df_asset['volume']
        df_asset['S-total_volume']=df_asset['volume'].rolling(window=155).sum()
        df_asset['S-total_value']=df_asset['vol_price'].rolling(window=155).sum()
        df_asset['S-realized_price']=df_asset['S-total_value']/df_asset['S-total_volume']
        
        fig,ax=plt.subplots(figsize=(12,6))
        STH, =ax.plot(df_asset['date'], df_asset['S-realized_price'], label='Short-Realized price', color='orange')
        close_price, =ax.plot(df_asset['date'], df_asset['close'], label='Close price', color='blue')
        ax.set_yscale('log')
        ax.get_yaxis().set_major_formatter(plt.ScalarFormatter())
        ax.ticklabel_format(axis='y', style='plain')
        ax.grid(which='both',linestyle='--',linewidth=0.5)
        mplcursors.cursor(STH, hover=True)
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.title(f'Short Realized price vs Close price for {asset_label}')  
        plt.legend()
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
        plt.xticks(rotation=45)
        plt.show()

    
    def Long_realized_price(self, asset_id,asset_label):
        df_asset=self.df[self.df['asset_id']==asset_id]
        df_asset['vol_price']=df_asset['close']*df_asset['volume']
        df_asset['total_volume']=df_asset['volume'].cumsum()
        df_asset['total_value']=df_asset['vol_price'].cumsum()
        df_asset['S-total_volume']=df_asset['volume'].rolling(window=155).sum()
        df_asset['S-total_value']=df_asset['vol_price'].rolling(window=155).sum()
        df_asset['L-total_value']=df_asset['total_value']-df_asset['S-total_value']
        df_asset['L-total_volume']=df_asset['total_volume']-df_asset['S-total_volume']

        df_asset['L-realized_price']=df_asset['L-total_value']/df_asset['L-total_volume']

        fig,ax =plt.subplots(figsize=(12,6))
        LTH,=ax.plot(df_asset['date'], df_asset['L-realized_price'], label='Long-Realized price', color='orange')
        close_price,=ax.plot(df_asset['date'], df_asset['close'], label='Close price', color='blue')
        ax.set_yscale('log')
        ax.get_yaxis().set_major_formatter(plt.ScalarFormatter())
        ax.ticklabel_format(axis='y', style='plain')
        ax.grid(which='both',linestyle='--',linewidth=0.5)
        mplcursors.cursor(LTH, hover=True)
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.title(f'Long Realized price vs Close price for {asset_label}')  
        plt.legend()
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
        plt.xticks(rotation=45)
        plt.show()
    

    def plot_bar_chart(self, asset1_id, asset2_id, asset1_label='BTC'):
        _, asset1_avg = self.get_asset_data(asset1_id)
        
        plt.figure(figsize=(12,6))
        colors = ['green' if val >= 0 else 'red' for val in asset1_avg['monthly_return']]
        plt.bar(asset1_avg['month'] , asset1_avg['monthly_return'], width=0.8, label=asset1_label, color=colors)
        plt.xticks(range(1,13))
        plt.xlabel('Month')
        plt.ylabel('Average Monthly Return')
        plt.title(f'Average monthly return: {asset1_label} ')
        plt.legend()
        plt.show()
    
    def plot_heatmap(self, asset_id,asset_label='BTC'):
        asset_df = self.df[self.df['asset_id'] == asset_id]
        monthly_prices2 = asset_df.groupby(['year', 'month'])['close'].agg(['first', 'last']).reset_index()
        monthly_prices2['monthly_return'] = (monthly_prices2['last'] - monthly_prices2['first']) / monthly_prices2['first']
        
        pivot_table = monthly_prices2.pivot(index='year', columns='month', values='monthly_return')
        
        cmap = ListedColormap(['red', 'green'])
        bounds = [-1e10, 0, 1e10]
        norm = BoundaryNorm(bounds, cmap.N)
        
        plt.figure(figsize=(10,6))
        sns.heatmap(
            pivot_table,
            annot=True, fmt=".2%",
            linewidths=0.5,
            linecolor='black',
            cmap=cmap,
            norm=norm,
            cbar=False
        )
        plt.title(f'Monthly return for {asset_label}. Red: Negative, Green: Positive')
        plt.xlabel('Month')
        plt.ylabel('Year')
        plt.show()

#------------------------FORECASTING------------------------
    def plot_prophet(self, asset_id,asset_label,holiday=None):
        df_asset = self.df[self.df['asset_id'] == asset_id][['date', 'close']]
        btc_prophet = df_asset[['date','close']].rename(columns={'date':'ds','close':'y'})
       
    
        model = Prophet(weekly_seasonality=True,yearly_seasonality=True,holidays=holiday)
        model.fit(btc_prophet)
        future = model.make_future_dataframe(periods=365)
        forecast = model.predict(future)

        
        fig,ax=plt.subplots(figsize=(10,6))
        ax.plot(forecast['ds'], forecast['yhat'], label='Forecast',linestyle='--')
        ax.plot(btc_prophet['ds'], btc_prophet['y'], label='Real data') 
        ax.fill_between(
            forecast['ds'],
            forecast['yhat_lower'],
            forecast['yhat_upper'],
            color='pink',
            alpha=0.3,
            label='confidence interval'
        ) 
        
        ax.grid(which='both',linestyle='--',linewidth=0.5)
        
        plt.title(f'Price forecast for {asset_label} using Prophet')
        plt.xlabel('Date')
        plt.ylabel('Close Price')
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
        plt.show()
if __name__ == "__main__":
    db_password = os.getenv("db_password")
    db_url = 'postgresql://postgres:*********@localhost:5432/finance_data'
    analyzer = FinancialDataAnalyzer(db_url)
    analyzer.load_data()
    analyzer.calculate_monthly_return()
    halving_dates = [
        "2016-07-09",  # 2nd Halving
        "2020-05-11",  # 3rd Halving
        "2024-04-20"   # 4th Halving
        ]
    halving=pd.DataFrame({'holiday':'halving','ds':pd.to_datetime(halving_dates),'lower_window':-60,'upper_window':60})
    analyzer.plot_prophet(asset_id=1,asset_label='BTC',holiday=halving)

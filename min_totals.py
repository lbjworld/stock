# coding: utf-8
import datetime
import logging

import pandas as pd
import tushare as ts

def datetime_before(days=30):
    dt = datetime.datetime.now() - datetime.timedelta(days=days)
    return int(dt.strftime("%Y%m%d"))

def get_last_trade(code):
    """获取最后一个交易日的价格信息"""
    date = datetime.datetime.now() - datetime.timedelta(days=1)
    days = 1
    while days <= 7:
        trade = ts.get_hist_data(code, start=date.strftime('%Y-%m-%d'), end=(date+datetime.timedelta(days=1)).strftime('%Y-%m-%d'))
        if not trade.empty:
            return trade
        date -= datetime.timedelta(days=days)
        days += 1
    return None

TOP_NUM = 10

# 获取股票基本信息
stock_info = ts.get_stock_basics()

# 过滤新股
stock_info = stock_info[stock_info.timeToMarket < datetime_before(30)]

# 过滤PE/市值为0的股票
stock_info = stock_info[stock_info.pe > 0.0]
stock_info = stock_info[stock_info.pe < 150.0]
stock_info = stock_info[stock_info.totals > 0.0]

# 按照市值排序
stock_info = stock_info.sort_values(by='totals', ascending=True)

selected = stock_info[:TOP_NUM]

codes = []
last_trades = []
opens = []
closes = []
for idx, series in selected.iterrows():
    code = idx
    try:
        df = get_last_trade(code)
        if not df.empty:
            last_trade_date = df.index[0]
            open_price = df.iat[0, 0]
            close_price = df.iat[0, 1]
            codes.append(code)
            last_trades.append(last_trade_date)
            opens.append(open_price) 
            closes.append(close_price)
    except:
        print "exception error"

last_prices_df = pd.DataFrame({'last_trade': last_trades, 'open': opens, 'close': closes}, index=codes)

stock_basic_df = selected.loc[:, ['name','industry','area','pe','outstanding','totals']]
print stock_basic_df.join(last_prices_df)



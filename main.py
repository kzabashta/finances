#!/usr/bin/env python

import itertools
import datetime
import pandas as pd
import matplotlib.pylab as plt
import sqlite3
import logging

from initializer import config_reader

plt.style.use('ggplot')

CLEAN_DATE = pd.Timestamp(datetime.date(2010,1,31))
COL_LIST = ['tx_amount', 'tx_description', 'account']

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

def save_accounts_figure(accounts):
    fig = plt.figure()
    fig.subplots_adjust(hspace=0.4, wspace=0.4)
    for i in range(0, len(accounts)):
        ax = fig.add_subplot(len(accounts) / 2 + 1, 2, i+1)
        transactions = accounts[i].transactions.groupby(accounts[i].transactions.index).sum()
        # Create a cumulate value of transactions
        transactions['cum_sum'] = transactions.tx_amount.cumsum()
        ax.set_title('%s has $%.2f as of %s' % (accounts[i].name, 
            transactions.cum_sum.iloc[-1], 
            transactions.index[-1].strftime('%Y/%m/%d')))

        x = transactions.index
        y = transactions['cum_sum']
        ax.plot(x, y)
    fig.set_size_inches(18.5, 18.5)
    fig.savefig("plots/accounts.png", dpi=100)

def save_combined_figure(df):
    df = df[df['tx_date'] >= CLEAN_DATE]
    x = df['tx_date']
    y = df['cum_sum']

    fig, ax = plt.subplots(nrows=1, ncols=1)
    ax.plot(x, y)
    fig.suptitle('Total holdings are $%.2f as of %s' % (df.cum_sum.iloc[-1], df.tx_date.iloc[-1].strftime('%Y/%m/%d')))
    plt.xlabel('Date')
    plt.ylabel('Holdings')
    fig.set_size_inches(18.5, 18.5)
    fig.savefig("plots/combined.png", dpi=100)
    plt.close(fig)

def save_interpolated_figure(df):
    df = df[df['tx_date'] >= CLEAN_DATE]
    x = df['tx_date']
    y = df['cum_sum']

    ts = pd.Series(y, index=x)
    ts = ts.resample("M").ffill().rolling(center=False, window=12, min_periods=1).mean()
    ts = ts.interpolate(method='piecewise_polynomial', order=3)

    fig, ax = plt.subplots(nrows=1, ncols=1)
    ax.plot(ts)
    fig.suptitle('Total holdings are $%.2f as of %s' % (df.cum_sum.iloc[-1], df.tx_date.iloc[-1].strftime('%Y/%m/%d')))
    plt.xlabel('Date')
    plt.ylabel('Holdings')
    fig.set_size_inches(18.5, 18.5)
    fig.savefig("plots/interpolated.png", dpi=100)
    plt.close(fig)

def save_to_db(df):
    conn = sqlite3.connect('transactions.db')
    df.to_sql('transactions', conn, if_exists='replace')
    df.to_csv('transactions.csv')
    conn.close()

if __name__ == '__main__':
    
    logging.basicConfig(level=logging.DEBUG,
                        format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s",
                        handlers=[logging.FileHandler("finances.log"),
                                  logging.StreamHandler()])
    config_reader = config_reader.ConfigReader('./statements/config.json')
    accounts = config_reader.get_configs()
    
    account_dfs = []

    for account in accounts:
        account_dfs.append(account.transactions[COL_LIST])

    # Process the combined transactions
    combined_tx = pd.concat(account_dfs)
    combined_tx.sort_index(inplace=True)
    save_to_db(combined_tx)

    # Group by the day the transaction occurred
    combined_tx = combined_tx.groupby(combined_tx.index).sum()
    # Create a cumulate value of transactions
    combined_tx['cum_sum'] = combined_tx.tx_amount.cumsum()

    combined_tx['tx_date'] = pd.to_datetime(combined_tx.index)

    save_accounts_figure(accounts)
    save_combined_figure(combined_tx)
    save_interpolated_figure(combined_tx)
    
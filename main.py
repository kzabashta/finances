#!/usr/bin/env python

import datetime
import pandas as pd
import matplotlib.pylab as plt

from initializer import config_reader

CLEAN_DATE = datetime.date(2016,1,31)

def save_accounts_figure(accounts):
    fig = plt.figure()
    fig.subplots_adjust(hspace=0.4, wspace=0.4)
    for i in range(0, len(accounts)):
        ax = fig.add_subplot(len(accounts) / 2 + 1, 2, i+1)
        ax.set_title('%s has $%.2f as of %s' % (accounts[i].name, 
            accounts[i].transactions.cum_sum.iloc[-1], 
            accounts[i].transactions.tx_date.iloc[-1].strftime('%Y/%m/%d')))

        x = accounts[i].transactions['tx_date']
        y = accounts[i].transactions['cum_sum']
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

if __name__ == '__main__':
    config_reader = config_reader.ConfigReader('./statements/config.json')
    accounts = config_reader.get_configs()
    
    dfs = []
    col_list = ['tx_date', 'tx_amount']

    for account in accounts:
        account.init_account()
        dfs.append(account.transactions[col_list])
    
    """
    combined_tx = pd.concat(dfs, ignore_index=True)
    combined_tx = combined_tx.sort_values('tx_date')
    combined_tx = combined_tx.set_index(pd.DatetimeIndex(combined_tx['tx_date']))
    combined_tx['cum_sum'] = combined_tx.tx_amount.cumsum()
    """
    combined_tx = pd.concat(dfs)
    combined_tx = combined_tx.sort_values('tx_date')
    combined_tx = combined_tx.set_index(pd.DatetimeIndex(combined_tx['tx_date']))
    combined_tx = combined_tx.groupby(combined_tx.index).sum()
    combined_tx['cum_sum'] = combined_tx.tx_amount.cumsum()
    combined_tx['tx_date'] = pd.to_datetime(combined_tx.index)
    save_accounts_figure(accounts)
    save_combined_figure(combined_tx)
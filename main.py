#!/usr/bin/env python

import pandas as pd
import matplotlib.pylab as plt

from initializer import config_reader

def save_combined_figure(df):
        x = df['tx_date']
        y = df['cum_sum']

        fig, ax = plt.subplots( nrows=1, ncols=1 )  # create figure & 1 axis
        ax.plot(x, y)
        fig.suptitle('Kosta has $%.2f as of %s' % (df.cum_sum.iloc[-1], df.tx_date.iloc[-1].strftime('%Y/%m/%d')))
        plt.xlabel('Date')
        plt.ylabel('Holdings')
        fig.savefig("plots/combined.png")   # save the figure to file
        plt.close(fig) 

if __name__ == '__main__':
    config_reader = config_reader.ConfigReader('./statements/config.json')
    accounts = config_reader.get_configs()
    
    dfs = []
    
    for account in accounts:
        account.init_account()
        dfs.append(account.transactions)
        account.save_figure()
    
    combined_tx = pd.concat(dfs, ignore_index=True)
    combined_tx = combined_tx.sort_values('tx_date')
    combined_tx = combined_tx.set_index(pd.DatetimeIndex(combined_tx['tx_date']))
    combined_tx['cum_sum'] = combined_tx.tx_amount.cumsum()
    save_combined_figure(combined_tx)
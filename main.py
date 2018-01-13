#!/usr/bin/env python

import itertools
import datetime
import pandas as pd
import matplotlib.pylab as plt
import statsmodels.api as sm
plt.style.use('dark_background')


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

def save_interpolated_figure(df):
    df = df[df['tx_date'] >= CLEAN_DATE]
    x = df['tx_date']
    y = df['cum_sum']

    ts = pd.Series(y, index=x)
    ts = ts.resample('D').mean()

    ts = ts.interpolate(method='spline', order=3)
    arima_predict(ts)
    
    fig, ax = plt.subplots(nrows=1, ncols=1)
    ax.plot(ts)
    fig.suptitle('Total holdings are $%.2f as of %s' % (df.cum_sum.iloc[-1], df.tx_date.iloc[-1].strftime('%Y/%m/%d')))
    plt.xlabel('Date')
    plt.ylabel('Holdings')
    fig.set_size_inches(18.5, 18.5)
    fig.savefig("plots/interpolated.png", dpi=100)
    plt.close(fig)

def arima_predict(ts):
    p = d = q = range(0, 2)
    pdq = list(itertools.product(p, d, q))
    seasonal_pdq = [(x[0], x[1], x[2], 12) for x in list(itertools.product(p, d, q))]
    lowest_pdq = lowest_seasonal_pdq = lowest_aic = None
    for param in pdq:
        for param_seasonal in seasonal_pdq:
            try:
                mod = sm.tsa.statespace.SARIMAX(ts,
                                                order=param,
                                                seasonal_order=param_seasonal,
                                                enforce_stationarity=False,
                                                enforce_invertibility=False)

                results = mod.fit()
                if lowest_aic is None:
                    lowest_aic = results.aic
                elif results.aic < lowest_aic:
                    lowest_pdq = pdq
                    lowest_seasonal_pdq = seasonal_pdq
                    lowest_aic = lowest_aic
            except:
                continue
    
    mod = sm.tsa.statespace.SARIMAX(y,
                                order=lowest_pdq,
                                seasonal_order=lowest_seasonal_pdq,
                                enforce_stationarity=False,
                                enforce_invertibility=False)

    results = mod.fit()

    print(results.summary().tables[1])

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
    save_interpolated_figure(combined_tx)
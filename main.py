#!/usr/bin/env python

import itertools
import datetime
import pandas as pd
import matplotlib.pylab as plt
import statsmodels.api as sm
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

    #arima_predict(ts)

def arima_predict(ts):
    p = d = q = range(0, 3)
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
                    lowest_pdq = param
                    lowest_seasonal_pdq = param_seasonal
                    lowest_aic = lowest_aic
            except:
                continue
    
    mod = sm.tsa.statespace.SARIMAX(ts,
                                order=lowest_pdq,
                                seasonal_order=lowest_seasonal_pdq,
                                enforce_stationarity=False,
                                enforce_invertibility=False)

    results = mod.fit()

    print(results.summary().tables[1])
    results.plot_diagnostics(figsize=(15, 12))
    plt.savefig("plots/ARIMA_diagnostic.png", dpi=100)
    plt.clf()
    print(ts)
    pred = results.get_prediction(start=pd.to_datetime('2017-6-30'), dynamic=True)
    pred_ci = pred.conf_int()

    
    ax = ts.plot(label='observed')
    pred.predicted_mean.plot(ax=ax, label='One-step ahead Forecast', alpha=.7)

    ax.fill_between(pred_ci.index,
                    pred_ci.iloc[:, 0],
                    pred_ci.iloc[:, 1], color='k', alpha=.2)

    ax.set_xlabel('Date')
    ax.set_ylabel('Wealth')
    plt.legend()
    plt.savefig("plots/forecast_validation.png", dpi=100)
    plt.clf()

    pred_uc = results.get_forecast(steps=24)
    pred_ci = pred_uc.conf_int()
    ax = ts.plot(label='observed', figsize=(20, 15))
    pred_uc.predicted_mean.plot(ax=ax, label='Forecast')
    ax.fill_between(pred_ci.index,
                    pred_ci.iloc[:, 0],
                    pred_ci.iloc[:, 1], color='k', alpha=.25)
    ax.set_xlabel('Date')
    ax.set_ylabel('Wealth')

    plt.legend()
    plt.savefig("plots/forecast.png", dpi=100)
    plt.clf()

def save_to_db(df):
    conn = sqlite3.connect('transactions.db')
    df.to_sql('transactions', conn, if_exists='replace')
    df.to_csv('transactions.csv')
    conn.close()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                    handlers=[logging.FileHandler("finances.log"),
                              logging.StreamHandler()])
    config_reader = config_reader.ConfigReader('./statements/config.json')
    accounts = config_reader.get_configs()
    
    account_dfs = []

    for account in accounts:
        logging.info('Processing account %s' % account)
        account.init_account()
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
    
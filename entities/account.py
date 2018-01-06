import glob
import pandas as pd
import matplotlib.pylab as plt

class Account():
    
    def __init__(self, name, tx_fpath=None, file_cols=None, alias_cols=None, is_header=None, amount_split=None):
        self.name = name
        self.tx_fpath = tx_fpath
        self.file_cols = file_cols
        self.alias_cols = alias_cols
        self.is_header = is_header
        self.amount_split = amount_split
    
    def init_account(self):
        dfs = []
        filenames = glob.glob(self.tx_fpath + "/*.csv")

        for filename in filenames:
            skiprows = [0] if self.is_header else None
            df = pd.read_csv(filename, names=self.file_cols, index_col=False, skiprows=skiprows, header=None)
            if self.amount_split:
                df['amount'] = df['amount_credit'] - df['amount_debit']
            df = df.rename(columns=self.alias_cols)
            df['tx_date'] = pd.to_datetime(df['tx_date'])
            df = df.set_index(pd.DatetimeIndex(df['tx_date']))
            df['cum_sum'] = df.tx_amount.cumsum()
            dfs.append(df)

        # Concatenate all data into one DataFrame
        self.transactions = pd.concat(dfs, ignore_index=True)
        x = self.transactions['tx_date']
        y = self.transactions['cum_sum']

        fig, ax = plt.subplots( nrows=1, ncols=1 )  # create figure & 1 axis
        ax.plot(x, y)
        fig.savefig("%s.png" % self.name)   # save the figure to file
        plt.close(fig) 
        
        #plt.plot(x, y)
        #plt.savefig("%s.png" % self.name)

    def __str__(self):
        return 'Account: %s' % self.name
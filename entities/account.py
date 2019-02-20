import glob
import logging
import pandas as pd
import matplotlib.pylab as plt

class Account():
    
    def __init__(self, name, tx_fpath=None, file_cols=None, 
                 alias_cols=None, is_header=None, amount_split=None, ratio=None):
        self.name = name
        self.tx_fpath = tx_fpath
        self.file_cols = file_cols
        self.alias_cols = alias_cols
        self.is_header = is_header
        self.amount_split = amount_split
        self.ratio = ratio
    
    def init_account(self):
        
        def get_amount(row):
            if pd.isnull(row['amount_credit']):
                return -row['amount_debit']
            else:
                return row['amount_credit']

        dfs = []
        filenames = glob.glob(self.tx_fpath + "/*.csv")

        for filename in filenames:
            logging.debug('Processing file %s' % filename)
            skiprows = 1 if self.is_header else None
            df = pd.read_csv(filename, names=self.file_cols, index_col=False, skiprows=skiprows, header=None)
            if self.amount_split:
                df['amount'] = df.apply(get_amount, axis=1)
            df = df.rename(columns=self.alias_cols)
            df['tx_date'] = pd.to_datetime(df['tx_date'])
            df['tx_amount'] *= self.ratio
            df['account'] = self.name
            df['hash'] = df.apply(lambda x: hash(tuple(x)), axis = 1)
            dfs.append(df)

        # Concatenate all data into one DataFrame
        self.transactions = pd.concat(dfs)
        self.transactions['tx_date'] = pd.to_datetime(self.transactions['tx_date'])
        self.transactions = self.transactions.set_index('tx_date')
        self.transactions.sort_index(inplace=True)
        
        # Remove duplicates
        deduped_txs = self.transactions.drop_duplicates(subset='hash')
        duplicate_count = self.transactions.shape[0] - deduped_txs.shape[0]
        self.transactions = deduped_txs
        if duplicate_count > 0:
            logging.warning('Found %i duplicates in %s account, they have been removed' 
                % (duplicate_count, self.name))

    def __str__(self):
        return 'Account: %s' % self.name
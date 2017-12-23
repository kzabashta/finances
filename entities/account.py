import glob
import pandas as pd

class Account():

    tx_fpath = None
    file_cols = None
    alias_cols = None

    def __init__(self, tx_fpath, file_cols, alias_cols):
        self.tx_fpath = tx_fpath
        self.file_cols = file_cols
        self.alias_cols = alias_cols

    def parse_file(self):
        dfs = []
        filenames = glob.glob(self.tx_fpath + "/*.csv")

        for filename in filenames:
            df = pd.read_csv(filename, names=self.file_cols, skiprows=[0])
            df = df.rename(columns=self.alias_cols)
            dfs.append(df)

        # Concatenate all data into one DataFrame
        return pd.concat(dfs, ignore_index=True)
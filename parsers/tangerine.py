import pandas as pd

from .generic_parser import GenericParser

class TangerineParser(GenericParser):

    name = None

    def __init__(self, name):
        self.name = name

    def parse_file(self, fpath):
        df = pd.read_csv(fpath, names=['date', 'transaction', 'name', 'memo', 'amount'], skiprows=[0])
        print(df)
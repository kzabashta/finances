"""
Sample config file:

{
    "tangerine_chequing": {
        "path": "tangerine/chequing.csv",
        "columns": ["date", "transaction", "name", "memo", "amount"],
        "aliases": {
            "tx_date": "date",
            "tx_description": "memo",
            "amount": "amount"
        }
    }
}

"""
import json

from entities.account import Account

class ConfigReader():
    
    # tx_fpath, file_cols, alias_cols
    config_fpath = None

    def __init__(self, config_fpath):
        self.config_fpath = config_fpath

    def get_configs(self):
        data = json.load(open(self.config_fpath))
        accounts = []
        for key, val in data.items():
            account = Account(key)
            account.tx_fpath = val['path']
            account.file_cols = val['columns']
            account.alias_cols = val['aliases']
            account.is_header = val['is_header']
            account.amount_split = val['amount_split']
            account.ratio = val['ratio']
            accounts.append(account)
        return accounts
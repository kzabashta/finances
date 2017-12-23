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
    
    config_fpath = None

    def __init__(self, config_fpath):
        self.config_fpath = config_fpath

    def get_configs(self):
        data = json.load(open(self.config_fpath))
        print(data)
#!/usr/bin/env python

from initializer import config_reader

if __name__ == '__main__':
    config_reader = config_reader.ConfigReader('./statements/config.json')
    accounts = config_reader.get_configs()
    for account in accounts:
        account.init_account()
        account.save_figure()
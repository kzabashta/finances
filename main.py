#!/usr/bin/env python

from initializer import config_reader

if __name__ == '__main__':
    config_reader = config_reader.ConfigReader('./statements/config.json')
    config_reader.get_configs()
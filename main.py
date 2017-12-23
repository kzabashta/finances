#!/usr/bin/env python

from parsers.tangerine import TangerineParser

tg = TangerineParser('chequing')
tg.parse_file('statements/tangerine/chequing.csv')
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Migrate Retrosheet Database.
Python 3.5.0+ (don't know about 3.4- and 2.x, sorry)
MySQL 5.6.0+ (don't know about 5.5- , sorry)
"""
import os
import click
from retrosheet_download import RetrosheetDownload
from retrosheet_mysql import RetrosheetMySql
from parse_csv import ParseCsv

__author__ = 'Shinichi Nakagawa'


@click.command()
@click.option('--from_year', '-f', default=2010, help='From Season')
@click.option('--to_year', '-t', default=2014, help='To Season')
@click.option('--configfile', '-c', default='config.ini', help='Config File')
def main(from_year, to_year, configfile):
    """
    :param from_year: Season(from)
    :param to_year: Season(to)
    :param configfile: Config file
    """
    # from <= to check
    if from_year > to_year:
        print('not From <= To({from_year} <= {to_year})'.format(from_year=from_year, to_year=to_year))
        raise SystemExit

    # Download
    RetrosheetDownload.run(from_year, to_year, configfile)

    # Parse Csv
    ParseCsv.run(from_year, to_year, configfile)

    # これをやらないと実行パスがずれる
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Migrate MySQL Database
    RetrosheetMySql.run(from_year, to_year, configfile)


if __name__ == '__main__':
    main()

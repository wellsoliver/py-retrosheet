#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Parse to Event Files, Game Logs and Roster.
Python 3.5.0+ (don't know about 3.4- and 2.x, sorry)
"""
import os
import subprocess
import click
from configparser import ConfigParser

__author__ = 'Shinichi Nakagawa'


class ParseCsv(object):

    CW_EVENT = '{chadwick_path}cwevent'
    CW_GAME = '{chadwick_path}cwgame'
    CW_EVENT_CMD = '{chadwick_path}cwevent -q -n -f 0-96 -x 0-62 -y {year} {year}*.EV* > {csvpath}/events-{year}.csv'
    CW_GAME_CMD = '{chadwick_path}cwgame -q -n -f 0-83 -y {year} {year}*.EV* > {csvpath}/games-{year}.csv'
    EV_FILE_PATTERN = '{path}/{year}*.EV*'
    EVENT_FILE = '{csvpath}/events-{year}.csv'
    GAME_FILE = '{csvpath}/games-{year}.csv'
    CSV_PATH = 'csv'

    def __init__(self):
        pass

    @classmethod
    def exists_chadwick(cls, chadwick_path: str):
        """
        exists chadwick binary
        :param chadwick_path: chadwick path
        :return: True or False
        """
        if os.path.exists(chadwick_path) \
            & os.path.exists(cls.CW_EVENT.format(chadwick_path=chadwick_path)) \
                & os.path.exists(cls.CW_GAME.format(chadwick_path=chadwick_path)):
            return True
        return False

    @classmethod
    def generate_files(
            cls,
            year: int,
            cmd_format: str,
            filename_format: str,
            chadwick_path: str,
            verbose: bool,
            csvpath: str
    ):
        """
        Generate CSV file
        :param year: Season
        :param cmd_format: Command format
        :param filename_format: Filename format
        :param chadwick_path: Chadwick Command Path
        :param verbose: Debug flg
        :param csvpath: csv output path
        """
        cmd = cmd_format.format(csvpath=csvpath, year=year, chadwick_path=chadwick_path)
        filename = filename_format.format(csvpath=csvpath, year=year)
        if os.path.isfile(filename):
            os.remove(filename)
        if verbose:
            print('calling {cmd}'.format(cmd=cmd))
        subprocess.call(cmd, shell=True)

    @classmethod
    def generate_retrosheet_files(
            cls,
            from_year: int,
            to_year: int,
            chadwick_path: str,
            verbose: str,
            csvpath: str
    ):
        """
        Generate CSV file
        :param from_year: Season(from)
        :param to_year: Season(to)
        :param chadwick_path: Chadwick Command Path
        :param verbose: Debug flg
        :param csvpath: csv output path
        """
        # generate files
        for year in [year for year in range(from_year, to_year + 1)]:
            # game
            ParseCsv.generate_files(
                year=year,
                cmd_format=ParseCsv.CW_GAME_CMD,
                filename_format=ParseCsv.GAME_FILE,
                chadwick_path=chadwick_path,
                verbose=verbose,
                csvpath=csvpath
            )
            # event
            ParseCsv.generate_files(
                year=year,
                cmd_format=ParseCsv.CW_EVENT_CMD,
                filename_format=ParseCsv.EVENT_FILE,
                chadwick_path=chadwick_path,
                verbose=verbose,
                csvpath=csvpath
            )

    @classmethod
    def run(cls, from_year: int, to_year: int, configfile: str):
        """
        :param from_year: Season(from)
        :param to_year: Season(to)
        :param configfile: Config file
        """
        config = ConfigParser()
        config.read(configfile)
        verbose = config.getboolean('debug', 'verbose')
        chadwick = config.get('chadwick', 'directory')
        path = os.path.abspath(config.get('download', 'directory'))
        csv_path = '{path}/csv'.format(path=path)

        # command exists check
        if not cls.exists_chadwick(chadwick):
            print('chadwick does not exist in {chadwick} - exiting'.format(chadwick=chadwick))
            raise SystemExit

        # make directory
        os.chdir(path)
        if not os.path.exists(ParseCsv.CSV_PATH):
            os.makedirs(ParseCsv.CSV_PATH)

        # generate files
        cls.generate_retrosheet_files(
            from_year=from_year,
            to_year=to_year,
            chadwick_path=chadwick,
            verbose=verbose,
            csvpath=csv_path
        )

        # change directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))


@click.command()
@click.option('--from_year', '-f', default=2001, help='From Season')
@click.option('--to_year', '-t', default=2014, help='To Season')
@click.option('--configfile', '-c', default='config.ini', help='Config File')
def create_retrosheet_csv(from_year, to_year, configfile):
    """
    :param from_year: Season(from)
    :param to_year: Season(to)
    :param configfile: Config file
    """
    # from <= to check
    if from_year > to_year:
        print('not From <= To({from_year} <= {to_year})'.format(from_year=from_year, to_year=to_year))
        raise SystemExit
    ParseCsv.run(from_year, to_year, configfile)


if __name__ == '__main__':
    create_retrosheet_csv()

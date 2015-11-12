#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Download .
Python 3.5.0+ (don't know about 3.4- and 2.x, sorry)
MySQL 5.6.0+ (don't know about 5.5- , sorry)
"""

import os
import click
from configparser import ConfigParser
from classes.fetcher import Fetcher
from queue import Queue

__author__ = 'Shinichi Nakagawa'


class RetrosheetDownload(object):

    FILES = (
        {
            'name': 'eventfiles',
            'config_flg': 'dl_eventfiles',
            'url': 'eventfiles_url',
            'pattern': r'({year})eve\.zip',
            'download_url': 'http://www.retrosheet.org/events/{year}eve.zip',
        },
        {
            'name': 'gamelogs',
            'config_flg': 'dl_gamelogs',
            'url': 'gamelogs_url',
            'pattern': r'gl({year})\.zip',
            'download_url': 'http://www.retrosheet.org/gamelogs/gl{year}.zip',
        }
    )

    def __init__(self, configfile: str):
        """
        initialize
        :param configfile: configuration file
        """
        # configuration
        self.config = ConfigParser()
        self.config.read(configfile)
        self.num_threads = self.config.getint('download', 'num_threads')
        self.path = self.config.get('download', 'directory')
        self.absolute_path = os.path.abspath(self.path)

    def download(self, queue):
        threads = []
        for i in range(self.num_threads):
            t = Fetcher(queue, self.absolute_path, {'verbose': self.config.get('debug', 'verbose')})
            t.start()
            threads.append(t)
        for thread in threads:
            thread.join()


    @classmethod
    def run(cls, from_year: int, to_year: int, configfile: str):
        client = RetrosheetDownload(configfile)
        urls = Queue()
        for year in range(from_year, to_year + 1):
            for _file in RetrosheetDownload.FILES:
                urls.put(_file['download_url'].format(year=year))

        client.download(urls)


@click.command()
@click.option('--from_year', '-f', default=2001, help='From Season')
@click.option('--to_year', '-t', default=2014, help='To Season')
@click.option('--configfile', '-c', default='config.ini', help='Config File')
def download(from_year, to_year, configfile):
    """
    :param from_year: Season(from)
    :param to_year: Season(to)
    :param configfile: Config file
    """
    # from <= to check
    if from_year > to_year:
        print('not From <= To({from_year} <= {to_year})'.format(from_year=from_year, to_year=to_year))
        raise SystemExit

    RetrosheetDownload.run(from_year, to_year, configfile)


if __name__ == '__main__':
    download()

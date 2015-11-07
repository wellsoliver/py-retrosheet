#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Migrate Database, Game Logs and Roster.
Python 3.5.0+ (don't know about 3.4- and 2.x, sorry)
MySQL 5.6.0+ (don't know about 5.5- , sorry)
"""
import os
import csv
import click
import sqlalchemy
from glob import glob
from configparser import ConfigParser, NoOptionError

__author__ = 'Shinichi Nakagawa'


class RetrosheetMySql(object):

    DATABASE_ENGINE = 'mysql+pymysql'
    ENGINE = '{engine}://{user}:{password}@{host}/{database}'
    MODULES = (
        {
            'table': 'teams',
            'mask': '{path}/TEAM{year}*',
            'select': 'SELECT * FROM teams WHERE team_id = {team_id}',
            'insert': 'INSERT INTO teams VALUES ({values})',
        },
        {
            'table': 'rosters',
            'mask': '{path}/*{year}*.ROS',
            'select': 'SELECT * FROM rosters WHERE year = {year} AND player_id = {player_id} AND team_tx = {team_tx}',
            'insert': 'INSERT INTO rosters VALUES ({values})',
        },
        {
            'table': 'events',
            'mask': '{path}/csv/events-{year}*.csv',
            'select': 'SELECT * FROM events WHERE game_id = {game_id} AND event_id = {event_id}',
            'insert': 'INSERT INTO events VALUES ({values})',
        },
        {
            'table': 'games',
            'mask': '{path}/csv/games-{year}*.csv',
            'select': 'SELECT * FROM games WHERE game_id = {game_id}',
            'insert': 'INSERT INTO games VALUES ({values})',
        },
    )

    def __init__(self, configfile: str):
        # configuration
        config = ConfigParser()
        config.read(configfile)
        self.path = os.path.abspath(config.get('download', 'directory'))
        # connection
        self.connection = self._generate_connection(config)

    @classmethod
    def _generate_connection(cls, config: ConfigParser):

        try:
            database_engine = cls.DATABASE_ENGINE
            database = config.get('database', 'database')

            host = config.get('database', 'host')
            user = config.get('database', 'user')
            password = config.get('database', 'password')
        except NoOptionError:
            print('Need to define engine, user, password, host, and database parameters')
            raise SystemExit

        db = sqlalchemy.create_engine(
            cls.ENGINE.format(
                engine=database_engine,
                user=user,
                password=password,
                host=host,
                database=database,
            )
        )

        return db.connect()

    def insert(self, year, csv_file):
        for row in csv.reader(open(csv_file)):
            print(row)

    def execute(self, year):
        for module in self.MODULES:
            for csv_file in glob(module['mask'].format(path=self.path, year=year)):
                self.insert(year, csv_file)

        self.connection.close()

    @classmethod
    def run(cls, from_year: int, to_year: int, configfile: str):
        client = RetrosheetMySql(configfile)
        for year in [year for year in range(from_year, to_year + 1)]:
            client.execute(year)


@click.command()
@click.option('--from_year', '-f', default=2001, help='From Season')
@click.option('--to_year', '-t', default=2014, help='To Season')
@click.option('--configfile', '-c', default='config.ini', help='Config File')
def migration(from_year, to_year, configfile):
    """
    :param from_year: Season(from)
    :param to_year: Season(to)
    :param configfile: Config file
    """
    # from <= to check
    if from_year > to_year:
        print('not From <= To({from_year} <= {to_year})'.format(from_year=from_year, to_year=to_year))
        raise SystemExit

    RetrosheetMySql.run(from_year, to_year, configfile)


if __name__ == '__main__':
    migration()

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
    TABLES = (
        {
            'name': 'teams',
            'header': False,
            'year': False,
            'mask': '{path}/TEAM{year}*',
            'select': "SELECT * FROM teams WHERE team_id = '{key_0}'",
            'where_index': [0],
            'insert': 'INSERT INTO teams VALUES {values}',
        },
        {
            'name': 'rosters',
            'header': False,
            'year': True,
            'mask': '{path}/*{year}*.ROS',
            'select': "SELECT * FROM rosters WHERE year = {year} AND player_id = '{key_0}' AND team_tx = '{key_1}'",
            'where_index': [0, 5],
            'insert': 'INSERT INTO rosters VALUES {values}',
        },
        {
            'name': 'games',
            'header': True,
            'year': False,
            'mask': '{path}/csv/games-{year}*.csv',
            'select': "SELECT * FROM games WHERE game_id = '{key_0}'",
            'where_index': [0],
            'insert': 'INSERT INTO games({columns}) VALUES {values}',
        },
        {
            'name': 'events',
            'header': True,
            'year': False,
            'mask': '{path}/csv/events-{year}*.csv',
            'select': "SELECT * FROM events WHERE game_id = '{key_0}' AND event_id = '{key_1}'",
            'where_index': [0, 96],
            'insert': 'INSERT INTO events({columns}) VALUES {values}',
        },
    )

    def __init__(self, configfile: str):
        """
        initialize
        :param configfile: configuration file
        """
        # configuration
        config = ConfigParser()
        config.read(configfile)
        self.path = os.path.abspath(config.get('download', 'directory'))
        self.record_check = config.getboolean('retrosheet_mysql', 'record_check')
        self.multiple_insert_rows = config.getint('retrosheet_mysql', 'multiple_insert_rows')
        # connection
        self.connection = self._generate_connection(config)

    @classmethod
    def _generate_connection(cls, config: ConfigParser):
        """
        generate database connection
        :param config: ConfigParser object
        :return:
        """

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

    @classmethod
    def _exists_record(cls, year: int, table: dict, csv_row: list, connection):
        where = {'key_{i}'.format(i=i): csv_row[v] for i, v in enumerate(table['where_index'])}
        where['year'] = year
        sql = table['select'].format(**where)
        res = connection.execute(sql)
        if res.rowcount > 0:
            return True
        return False

    def _multiple_insert(self, query: str, columns: list, values: list):
        params = {
            'columns': columns,
            'values': ', '.join(values),
        }
        sql = query.format(**params)
        try:
            self.connection.execute(sql)
        except Exception as e:
            print(e)
            raise SystemExit

    def _create_record(self, year: int, csv_file: str, table: dict):
        reader = csv.reader(open(csv_file))
        headers = []
        values = []
        if table['header']:
            headers = next(reader)
        columns = ', '.join(headers)
        for row in reader:
            # Record Exists Check
            if self.record_check and RetrosheetMySql._exists_record(year, table, row, self.connection):
                continue
            # append record values
            if table['year']: row.insert(0, str(year))
            values.append('("{rows}")'.format(rows='", "'.join(row)))
            if len(values) == self.multiple_insert_rows:
                # inserts
                self._multiple_insert(table['insert'], columns, values)
                values = []
        if len(values) > 0:
            # inserts
            self._multiple_insert(table['insert'], columns, values)

    def execute(self, year: int):
        for table in self.TABLES:
            for csv_file in glob(table['mask'].format(path=self.path, year=year)):
                self._create_record(year, csv_file, table)

    @classmethod
    def run(cls, from_year: int, to_year: int, configfile: str):
        client = RetrosheetMySql(configfile)
        for year in range(from_year, to_year + 1):
            client.execute(year)
        client.connection.close()


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

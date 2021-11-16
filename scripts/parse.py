import os
import subprocess
import configparser
import sqlalchemy
import csv
import glob
import re
import getopt
import sys


def connect(config):
    try:
        ENGINE = config.get('database', 'engine')
        DATABASE = config.get('database', 'database')

        HOST = None if not config.has_option('database', 'host') else config.get('database', 'host')
        USER = None if not config.has_option('database', 'user') else config.get('database', 'user')
        SCHEMA = None if not config.has_option('database', 'schema') else config.get('database', 'schema')
        PASSWORD = None if not config.has_option('database', 'password') else config.get('database', 'password')
    except configparser.NoOptionError:
        print ('Need to define engine, user, password, host, and database parameters')
        raise SystemExit

    if ENGINE == 'sqlite':
        dbString = ENGINE + ':///%s' % (DATABASE)
    else:
        if USER and PASSWORD:
            dbString = ENGINE + '://%s:%s@%s/%s' % (USER, PASSWORD, HOST, DATABASE)
        elif USER:
            dbString = ENGINE + '://%s@%s/%s' % (USER, HOST, DATABASE)
        else:
            dbString = ENGINE + '://%s/%s' % (HOST, DATABASE)
        
    db = sqlalchemy.create_engine(dbString)
    conn = db.connect()
    
    return conn


def parse_rosters(file, conn, bound_param):
    print ("processing %s" % file)
    
    try:
        year = re.search(r"\d{4}", os.path.basename(file)).group(0)
    except:
        print ('cannot get year from roster file %s' % file)
        return None

    reader = csv.reader(open(file))

    for row in reader:
        row.insert(0, year) # Insert year

        sql = 'SELECT * FROM rosters WHERE year = %s AND player_id = %s AND team_tx = %s'
        res = conn.execute(sql, [row[0], row[1], row[6]])
        
        if res.rowcount == 1:
            continue
        
        sql = "INSERT INTO rosters VALUES (%s)" % ", ".join([bound_param] * len(row))
        conn.execute(sql, row)
    
    return True


def parse_teams(file, conn, bound_param):
    print ("processing %s" % file)

    reader = csv.reader(open(file))
    for row in reader:
        if len(row) != 4:
            continue

        sql = 'SELECT * FROM teams WHERE team_id = %s'
        res = conn.execute(sql, [row[0]])
        
        if res.rowcount == 1:
            continue

        sql = "INSERT INTO teams VALUES (%s)" % ", ".join([bound_param] * len(row))
        conn.execute(sql, row)


def parse_games(file, conn, bound_param):
    print ("processing %s" % file)

    try:
        year = re.search(r"\d{4}", os.path.basename(file)).group(0)
    except:
        print ('cannot get year from game file %s' % file)
        return None
 
    if conn.engine.driver == 'psycopg2':
        conn.execute('DELETE FROM games WHERE game_id LIKE \'%%' + year + '%%\'')
        conn.execute('COPY games FROM %s WITH CSV HEADER', file)
    else:
        reader = csv.reader(open(file))
        headers = reader.next()
        for row in reader:
            sql = 'SELECT * FROM games WHERE game_id = %s'
            res = conn.execute(sql, [row[0]])
            
            if res.rowcount == 1:
                continue

            sql = 'INSERT INTO games(%s) VALUES(%s)' % (','.join(headers), ','.join([bound_param] * len(headers)))
            conn.execute(sql, row)


def parse_events(file, conn, bound_param):
    print ("processing %s" % file)

    try:
        year = re.search(r"\d{4}", os.path.basename(file)).group(0)
    except:
        print ('cannot get year from event file %s' % file)
        return None

    if conn.engine.driver == 'psycopg2':
        conn.execute('DELETE FROM events WHERE game_id LIKE \'%%' + year + '%%\'')
        conn.execute('COPY events FROM %s WITH CSV HEADER', file)
        conn.execute('COMMIT')
    else:
        reader = csv.reader(open(file))
        headers = reader.next()
        for row in reader:
            sql = 'SELECT * FROM events WHERE game_id = %s AND event_id = %s'
            res = conn.execute(sql, [row[0], row[96]])
            
            if res.rowcount == 1:
                return True

            sql = 'INSERT INTO events(%s) VALUES(%s)' % (','.join(headers), ','.join([bound_param] * len(headers)))
            conn.execute(sql, row)

def env_to_config(config):
    """If certain environment variables are set have them override existing
    settings in the `config` object."""
    cfg_items = [{'section': 'database', 'option': 'engine'},
                 {'section': 'database', 'option': 'host'},
                 {'section': 'database', 'option': 'database'},
                 {'section': 'database', 'option': 'user'},
                 {'section': 'database', 'option': 'password'},
                 {'section': 'download', 'option': 'directory'},
                 {'section': 'download', 'option': 'num_threads'},
                 {'section': 'download', 'option': 'dl_eventfiles'},
                 {'section': 'download', 'option': 'dl_gamelogs'},
                 {'section': 'chadwick', 'option': 'directory'},
                 {'section': 'retrosheet', 'option': 'eventfiles_url'},
                 {'section': 'retrosheet', 'option': 'gamelogs_url'},
                 {'section': 'debug', 'option': 'verbose'}]
    for item in cfg_items:
        env_var_name = (item['section']+'_'+item['option']).upper()
        env_var_value = os.environ.get(env_var_name)
        if env_var_value is not None:
            config.set(item['section'], item['option'], env_var_value)
    return config

def main():
    config = configparser.ConfigParser()
    config.read_file(open('config.ini'))
    config = env_to_config(config)

    try:
        conn = connect(config)
    except Exception as e:
        print('Cannot connect to database: %s' % e)
        raise SystemExit
    
    useyear     = False # Use a single year or all years
    verbose     = config.getboolean('debug', 'verbose')
    chadwick    = config.get('chadwick', 'directory')
    path        = os.path.abspath(config.get('download', 'directory'))
    csvpath     = '%s/csv' % path
    files       = []
    years       = []
    opts, args  = getopt.getopt(sys.argv[1:], "y:")
    bound_param = '?' if config.get('database', 'engine') == 'sqlite' else '%s'
    modules     = ['teams', 'rosters', 'events', 'games'] # items to process

    if not os.path.exists(chadwick) \
        or not os.path.exists('%s/cwevent' % chadwick) \
        or not os.path.exists('%s/cwgame' % chadwick):
        print ('chadwick does not exist in %s - exiting' % chadwick)
        raise SystemExit
    
    os.chdir(path) # Chadwick seems to need to be in the directory
    
    if not os.path.exists('csv'):
        os.makedirs('csv')

    for file in glob.glob("%s/*.EV*" % path):
        files.append(file)

    if len(opts) > 0:
        for o, a in opts:
            if o == '-y':
                yearfile = '%s/%s*.EV*' % (path, a)
                if len(glob.glob(yearfile)) > 0 and a not in years:
                    years.append(int(a))
                    useyear = True
    else:
        for file in files:
            year = re.search(r"^\d{4}", os.path.basename(file)).group(0)
            if year not in years:
                years.append(int(year))

    for year in years:
        if not os.path.isfile('%s/events-%d.csv' % (csvpath, year)):
            cmd = "%s/cwevent -q -n -f 0-96 -x 0-62 -y %d %d*.EV* > %s/events-%d.csv" % (chadwick, year, year, csvpath, year)
            if(verbose):
                print ("calling '" + cmd + "'")
            subprocess.call(cmd, shell=True)

        if not os.path.isfile('%s/games-%d.csv' % (csvpath, year)):
            cmd = "%s/cwgame -q -n -f 0-83 -y %d %d*.EV* > %s/games-%d.csv" % (chadwick, year, year, csvpath, year)
            if(verbose):
                print ("calling '" + cmd + "'")
            subprocess.call(cmd, shell=True)

    if 'teams' in modules:
        mask = "TEAM*" if not useyear else "TEAM%s*" % years[0]
        for file in glob.glob(mask):
            parse_teams(file, conn, bound_param)

    if 'rosters' in modules:
        mask = "*.ROS" if not useyear else "*%s*.ROS" % years[0]
        for file in glob.glob(mask):
            parse_rosters(file, conn, bound_param)

    if 'games' in modules:
        mask = '%s/games-*.csv' % csvpath if not useyear else '%s/games-%s*.csv' % (csvpath, years[0])
        for file in glob.glob(mask):
            parse_games(file, conn, bound_param)

    if 'events' in modules:
        mask = '%s/events-*.csv' % csvpath if not useyear else '%s/events-%s*.csv' % (csvpath, years[0])
        for file in glob.glob(mask):
            parse_events(file, conn, bound_param)

    conn.close()


if __name__ == '__main__':
    main()

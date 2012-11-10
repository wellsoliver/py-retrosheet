import os
import subprocess
import ConfigParser
import threading
import Queue
import sqlalchemy
import csv
import time
import glob
import re

config = ConfigParser.ConfigParser()
config.readfp(open('config.ini'))

num_threads = config.getint('processing', 'num_threads')
path = config.get('download', 'directory')
CHADWICK = config.get('chadwick', 'directory')

options = {}
options['verbose'] = config.get('debug', 'verbose')

try:
    ENGINE = config.get('database', 'engine')
    DATABASE = config.get('database', 'database')

    HOST = None if not config.has_option('database', 'host') else config.get('database', 'host')
    USER = None if not config.has_option('database', 'user') else config.get('database', 'user')
    SCHEMA = None if not config.has_option('database', 'schema') else config.get('database', 'schema')
    PASSWORD = None if not config.has_option('database', 'password') else config.get('database', 'password')

except ConfigParser.NoOptionError:
    print 'Need to define engine, user, password, host, and database parameters'
    raise SystemExit

if ENGINE == 'sqlite':
    # SQLAlchemy connect string uses a third slash for SQLite
    separator = ':///'

    # SQLite uses a different symbol for bound parameters than MySQL/PostgreSQL
    bound_param = '?'
else:
    separator = '://'
    bound_param = '%s'

if USER and PASSWORD:
    # MySQL & PostgreSQL case
    dbString = ENGINE + separator + '%s:%s@%s/%s' % (USER, PASSWORD, HOST, DATABASE)
else:
    # SQLite case
    dbString = ENGINE + separator + '%s' % (DATABASE)

try:
    db = sqlalchemy.create_engine(dbString)
    conn = db.connect()
    if(options['verbose']):
        print 'connected to database.'
except:
    print 'Cannot connect to database'
    raise SystemExit


class Parser(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while 1:
            try:
                year = self.queue.get_nowait()
            except Queue.Empty:
                break

            cmd = "%s/cwevent -q -n -f 0-96 -x 0-60 -y %d %d*.EV* > events-%d.csv" % (CHADWICK, year, year, year)
            if(options['verbose']):
                print "calling '" + cmd + "'"

            subprocess.call(cmd, shell=True)
            cmd = "%s/cwgame -q -n -f 0-83 -y %d %d*.EV* > games-%d.csv" % (CHADWICK, year, year, year)
            if(options['verbose']):
                print "calling '" + cmd + "'"

            subprocess.call(cmd, shell=True)

            for file in glob.glob("%d*" % year):
                os.remove(file)

print "processing game files..."
queue = Queue.Queue()
years = []
threads = []
absolute_path = os.path.abspath(path)
os.chdir(absolute_path)

for file in glob.glob("%s/*.EV*" % absolute_path):
    year = re.search(r"^\d{4}", os.path.basename(file)).group(0)
    if year not in years:
        queue.put(int(year))
        years.append(year)

for i in range(num_threads):
    t = Parser(queue)
    t.start()
    threads.append(t)

# finishing processing games before processing rosters
for thread in threads:
    thread.join()

print "processing rosters..."
for file in glob.glob("*.ROS"):
    filename = os.path.basename(file)
    f = open(file, "r")

    try:
        team, year = re.findall(r"(^\w{3})(\d{4}).+?$", filename)[0]
    except IndexError:
        print 'invalid file: ' + filename
        continue

    if(options['verbose']):
        print 'processing ' + filename

    for line in f.readlines():

        if line.strip() == "":
            continue

        info = line.strip().replace('"', '').split(",")

        info.insert(0, team)
        info.insert(0, year)

        # wacky '\x1a' ASCII characters, probably some better way of handling this
        if len(info) == 3:
            continue

        # ROSTERS table has nine columns, let's fill it out
        if len(info) < 9:
            for i in range(9 - len(info)):
                info.append(None)

        sql = "INSERT INTO rosters VALUES (%s)" % ", ".join([bound_param] * len(info))
        conn.execute(sql, info)

print "processing teams..."
for file in glob.glob("TEAM*"):
    f = open(file, "r")

    try:
        year = re.findall(r"^TEAM(\d{4})$", os.path.basename(file))[0]
    except:
        continue

    for line in f.readlines():

        if line.strip() == "":
            continue

        info = line.strip().replace('"', '').split(",")
        info.insert(0, year)

        if len(info) < 5:
            continue

        sql = "INSERT INTO teams VALUES (%s)" % ", ".join([bound_param] * len(info))
        conn.execute(sql, info)


for file in glob.glob("events-*.csv"):
    print "processing %s" % file
    reader = csv.reader(open(file))
    headers = reader.next()
    for row in reader:
        sql = 'INSERT INTO events(%s) VALUES(%s)' % (','.join(headers), ','.join([bound_param] * len(headers)))
        conn.execute(sql, row)

for file in glob.glob("games-*.csv"):
    print "processing %s" % file
    reader = csv.reader(open(file))
    headers = reader.next()
    for row in reader:
        sql = 'INSERT INTO games(%s) VALUES(%s)' % (','.join(headers), ','.join([bound_param] * len(headers)))
        conn.execute(sql, row)

# cleanup!
for file in glob.glob("%s/*" % absolute_path):
    os.remove(file)

os.rmdir(absolute_path)
conn.close()

elapsed = (time.time() - start)
print "%d seconds!" % elapsed
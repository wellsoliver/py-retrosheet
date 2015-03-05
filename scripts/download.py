import urllib
import os
import ConfigParser
import Queue
import re
import getopt
import sys

from classes.fetcher import Fetcher

# initialize variables / set defaults
YEAR = False

# load configs
config = ConfigParser.ConfigParser()
config.readfp(open('config.ini'))

# load settings into separate var
# can this be replaced by config var in the future?
options = {}
options['verbose'] = config.get('debug', 'verbose')

# load and evaluate download directory
path = config.get('download', 'directory')
absolute_path = os.path.abspath(path)

# test for existence of download directory
# create if does not exist
try:
    os.chdir(absolute_path)
except OSError:
    print "Directory %s does not exist, creating..." % absolute_path
    os.makedirs(absolute_path)


# parse options list. Look for -y <year> or --year <year> options
# exit on unrecognized option or option without argument
try:
    opts, args = getopt.getopt(sys.argv[1:], "y:", ["year="])
except getopt.GetoptError as e:
    print 'Invalid arguments. Exiting.'
    raise SystemExit

# set year if passed in
for o, a in opts:
    if o in ('-y', '--year'): YEAR = a

# log next action
if YEAR:
    print "fetching retrosheet files for year %s..." % YEAR
else:
    print "fetching retrosheet files..."

# parse retrosheet page for file and add urls to the queue
queue = Queue.Queue()
retrosheet_url = config.get('retrosheet', 'url')
pattern = r'(\d{4}?)eve\.zip'
for match in re.finditer(pattern, urllib.urlopen(retrosheet_url).read(), re.S):
    if YEAR and match.group(1) != YEAR: continue
    url = 'http://www.retrosheet.org/events/%seve.zip' % match.group(1)
    queue.put(url)

# set threads
threads = []
num_threads = config.getint('download', 'num_threads')

for i in range(num_threads):
    t = Fetcher(queue, absolute_path, options)
    t.start()
    threads.append(t)

# finish fetching before processing events into CSV
for thread in threads:
    thread.join()

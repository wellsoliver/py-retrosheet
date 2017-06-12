import os
import requests
try:
    # Python 3.x
    from configparser import ConfigParser
    import queue
except ImportError:
    # Python 2.x
    from ConfigParser import ConfigParser
    import Queue as queue

import re
import getopt
import sys
from classes.fetcher import Fetcher

# load configs
config = ConfigParser()
config.read('config.ini')

# initialize variables / set defaults
queue = queue.Queue()
YEAR = False
threads = []
num_threads = config.getint('download', 'num_threads')

# load settings into separate var
# can this be replaced by config var in the future?
options = {}
options['verbose'] = config.getboolean('debug', 'verbose')

# load and evaluate download directory
path = config.get('download', 'directory')
absolute_path = os.path.abspath(path)

# test for existence of download directory
# create if does not exist
try:
    os.chdir(absolute_path)
except OSError:
    print("Directory %s does not exist, creating..." % absolute_path)
    os.makedirs(absolute_path)


# parse options list. Look for -y <year> or --year <year> options
# exit on unrecognized option or option without argument
try:
    opts, args = getopt.getopt(sys.argv[1:], "y:", ["year="])
except getopt.GetoptError as e:
    print('Invalid arguments. Exiting.')
    raise SystemExit

# set year if passed in
for o, a in opts:
    if o in ('-y', '--year'): YEAR = a
    
##################################
# Queue Event Files for Download #
##################################

if config.getboolean('download', 'dl_eventfiles'):

    # log next action
    if YEAR:
        print("Queuing up Event Files for download (%s only)." % YEAR)
    else:
        print("Queuing up Event Files for download.")

    # parse retrosheet page for files and add urls to the queue
    eventfiles_requests = requests.get(config.get('retrosheet', 'eventfiles_url'))
    pattern = r'(\d{4}?)eve\.zip'
    matches = re.finditer(pattern, eventfiles_requests.text, re.S)
    for match in matches:
    
        # if we are looking for a year and this isnt the one, skip it
        if YEAR and match.group(1) != YEAR:
            continue
        
        # compile absolute url and add to queue
        url = 'http://www.retrosheet.org/events/%seve.zip' % match.group(1)
        queue.put(url)

#################################
# Queue Game Logs for Download #
#################################

if config.getboolean('download', 'dl_gamelogs'):

    # log next action
    if YEAR:
        print("Queuing up Game Logs for download (%s only)." % YEAR)
    else:
        print("Queuing up Game Logs for download.")

    # parse retrosheet page for files and add urls to the queue
    egamelogs_requests = requests.get(config.get('retrosheet', 'gamelogs_url'))
    pattern = r'gl(\d{4})\.zip'
    matches = re.finditer(pattern, egamelogs_requests.text, re.S)
    for match in matches:
    
        # if we are looking for a year and this isnt the one, skip it
        if YEAR and match.group(1) != YEAR:
            continue
        
        # compile absolute url and add to queue
        url = 'http://www.retrosheet.org/gamelogs/gl%s.zip' % match.group(1)
        queue.put(url)

##################
# Download Files #
##################
        
# spin up threads
for i in range(num_threads):
    t = Fetcher(queue, absolute_path, options)
    t.start()
    threads.append(t)

# wait for all threads to finish
for thread in threads:
    thread.join()

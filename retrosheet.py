#!/usr/bin/env python
import urllib
import os
import subprocess
import threading
import Queue
import zipfile
import glob
import tempfile
import re
import time
import MySQLdb
import sys

THREADS = 20
RETROSHEET_URL = "http://www.retrosheet.org/game.htm"
CHADWICK = "/usr/local/bin/"
CNF="/home/wells/.my.cnf"
DB="retrosheet"

db = MySQLdb.connect(host="localhost", read_default_file=CNF, db=DB)

class Parser(threading.Thread):
	def __init__(self, queue):
		threading.Thread.__init__(self)
		self.queue = queue
	
	def run(self):
		while 1:
			try:
				year = self.queue.get_nowait()
			except Queue.Empty:
				break;

			cmd = "%s/cwevent -q -f 0-96 -x 0-54 -y %d %d*.EV* > events-%d.csv" % (CHADWICK, year, year, year)
			subprocess.call(cmd, shell=True)
			cmd = "%s/cwgame -q -f 0-83 -y %d %d*.EV* > games-%d.csv" % (CHADWICK, year, year, year)
			subprocess.call(cmd, shell=True)
			
			for file in glob.glob("%d*" % year):
				os.remove(file)
			
class Fetcher(threading.Thread):
	def __init__(self, queue, path):
		threading.Thread.__init__(self)
		self.queue = queue
		self.path = path
		
	def run(self):
		while 1:
			try:
				url = self.queue.get_nowait()
			except Queue.Empty:
				break;

			f = "%s/%s" % (self.path, os.path.basename(url))
			urllib.urlretrieve(url, f)
			
			if (zipfile.is_zipfile(f)):
				zip = zipfile.ZipFile(f, "r")
				zip.extractall(self.path)

			os.remove(f)

start = time.time()
path = tempfile.mkdtemp()
os.chdir(path)

cursor = db.cursor()

print "fetching retrosheet files..."
queue = Queue.Queue()
pattern = r'href="(?P<url>http://www.retrosheet.org/(?P<year>\d{4})/\d{4}(?P<league>\w{2}).htm)"'
for match in re.finditer(pattern, urllib.urlopen(RETROSHEET_URL).read(), re.S):
	url = "http://www.retrosheet.org/%s/%s%s.zip" % (match.group("year"), match.group("year"), match.group("league"))
	queue.put(url)

threads = []
for i in range(THREADS):
	t = Fetcher(queue, path)
	t.start()
	threads.append(t)

# be sure to finish fetching before parsing starts
for thread in threads:
	thread.join()
	
print "processing game files..."
queue = Queue.Queue()

years = []
for file in glob.glob("%s/*.EV*" % path):
	year = re.search(r"^\d{4}", os.path.basename(file)).group(0)
	if year not in years:
		queue.put(int(year))
		years.append(year)

for i in range(THREADS):
	t = Parser(queue)
	t.start()
	threads.append(t)

# finishing parsing before importing
for thread in threads:
	thread.join()

print "processing rosters..."
for file in glob.glob("*.ROS"):
	f = open(file, "r")
	
 	team, year = re.findall(r"(^\w{3})(\d{4}).+?$", os.path.basename(file))[0]
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
			for i in range (9 - len(info)):
				info.append('')
			
		sql = "INSERT INTO ROSTERS VALUES (%s)" % ", ".join(["%s"] * len(info))
		cursor.execute(sql, info)
		db.commit()

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

		sql = "INSERT INTO TEAMS VALUES (%s)" % ", ".join(["%s"] * len(info))
		cursor.execute(sql, info)
		db.commit()

for file in glob.glob("events-*.csv"):
	print "processing %s" % file
	sql = "LOAD DATA LOCAL INFILE \"%s\" INTO TABLE EVENTS FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' LINES TERMINATED BY '\n'" % file
	cursor.execute(sql)
	db.commit()

for file in glob.glob("games-*.csv"):
	print "processing %s" % file
	sql = "LOAD DATA LOCAL INFILE \"%s\" INTO TABLE GAMES FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' LINES TERMINATED BY '\n'" % file
	cursor.execute(sql)
	db.commit()

cursor.close()
db.close()

# cleanup!
for file in glob.glob("%s/*" % path):
	os.remove(file)

os.rmdir(path)
	
elapsed = (time.time() - start)
print "%d seconds!" % elapsed

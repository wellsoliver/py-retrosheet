import urllib
import os
import ConfigParser
import threading
import Queue
import zipfile
import re


config = ConfigParser.ConfigParser()
config.readfp(open('config.ini'))

options = {}
options['verbose'] = config.get('debug', 'verbose')


class Fetcher(threading.Thread):
    def __init__(self, queue, path, options):
        threading.Thread.__init__(self)
        self.queue = queue
        self.path = path
        self.options = options

    def run(self):
        while 1:
            try:
                url = self.queue.get_nowait()
            except Queue.Empty:
                break

            filename = os.path.basename(url)

            if(options['verbose']):
                print "fetching " + filename

            f = "%s/%s" % (self.path, filename)
            urllib.urlretrieve(url, f)

            if (zipfile.is_zipfile(f)):
                zip = zipfile.ZipFile(f, "r")
                zip.extractall(self.path)
                if(options['verbose']):
                    print "extracting " + filename

            os.remove(f)

path = config.get('download', 'directory')
absolute_path = os.path.abspath(path)
try:
    os.chdir(absolute_path)
except OSError:
    print "Directory '" + absolute_path + "' does not exist."
    raise SystemExit

print "fetching retrosheet files..."
queue = Queue.Queue()
retrosheet_url = config.get('retrosheet', 'url')
pattern = r'(\d{4}?)eve\.zip'
for match in re.finditer(pattern, urllib.urlopen(retrosheet_url).read(), re.S):
    url = 'http://www.retrosheet.org/events/%seve.zip' % match.group(1)
    queue.put(url)

threads = []
num_threads = config.getint('download', 'num_threads')

for i in range(num_threads):
    t = Fetcher(queue, absolute_path, options)
    t.start()
    threads.append(t)

# finish fetching before processing events into CSV
for thread in threads:
    thread.join()

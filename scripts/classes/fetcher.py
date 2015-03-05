import urllib
import os
import threading
import Queue
import zipfile

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

            if(self.options['verbose']):
                print "fetching " + filename

            f = "%s/%s" % (self.path, filename)
            urllib.urlretrieve(url, f)

            if (zipfile.is_zipfile(f)):
                zip = zipfile.ZipFile(f, "r")
                zip.extractall(self.path)
                if(self.options['verbose']):
                    print "extracting " + filename

            os.remove(f)
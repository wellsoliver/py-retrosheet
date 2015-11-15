import os
import threading
from distutils.util import strtobool
try:
    # Python 3.x
    from urllib.request import urlretrieve
    import queue
except ImportError:
    # Python 2.x
    import Queue as queue
    from urllib import urlretrieve
import zipfile


class Fetcher(threading.Thread):

    def __init__(self, q, path, options):
        threading.Thread.__init__(self)
        self.q = q
        self.path = path
        self.verbose = strtobool(options['verbose'])

    def run(self):
    
        # loop
        while 1:
        
            # grab something from the queue
            # exit if queue empty
            try:
                url = self.q.get_nowait()
            except queue.Empty:
                break

            # extract file name from url
            filename = os.path.basename(url)

            # log
            if self.verbose:
                print("Fetching " + filename)

            # determine the local path
            f = "%s/%s" % (self.path, filename)
            
            # save file
            urlretrieve(url, f)

            # is this a zip file?
            if zipfile.is_zipfile(f):
                # log
                if self.verbose:
                    print("Zip file detected. Extracting " + filename)
                # extract the zip file
                zip = zipfile.ZipFile(f, "r")
                zip.extractall(self.path)

                # remove the zip file
                os.remove(f)

import urllib.request
import urllib.parse
import urllib.error
import os
import threading
import queue
import zipfile


class Fetcher(threading.Thread):

    def __init__(self, queue, path, options):
        threading.Thread.__init__(self)
        self.queue = queue
        self.path = path
        self.options = options

    def run(self):
    
        # loop
        while 1:
        
            # grab something from the queue
            # exit if queue empty
            try:
                url = self.queue.get_nowait()
            except queue.Empty:
                break

            # extract file name from url
            filename = os.path.basename(url)

            # log
            if(self.options['verbose']):
                print("Fetching " + filename)

            # determine the local path
            f = "%s/%s" % (self.path, filename)
            
            # save file
            urllib.request.urlretrieve(url, f)

            # is this a zip file?
            if (zipfile.is_zipfile(f)):
            
                #log
                if(self.options['verbose']):
                    print("Zip file detected. Extracting " + filename)
                
                # extract the zip file
                zip = zipfile.ZipFile(f, "r")
                zip.extractall(self.path)

                # remove the zip file
                os.remove(f)
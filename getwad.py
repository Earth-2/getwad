# For downloading wads from /idgames and putting them in useful places

import os
import re
from bs4 import BeautifulSoup
import urllib2
import urllib
import sys
from progressbar import *

# Progress bar related things
widgets = ['Progress: ', Percentage(), ' ', Bar(marker=RotatingMarker()), ' ', ETA(), ' at ', FileTransferSpeed()]
pbar = ProgressBar(widgets=widgets)
def dlProgress(count, blockSize, totalSize):
    if pbar.maxval is None:
        pbar.maxval = totalSize
        pbar.start()

    pbar.update(min(count*blockSize, totalSize))


wadlink = list()    # list of download links
lcount = 0          # number of download links available

startdir = os.getcwd()

wadurl = raw_input("Enter URL for /idgames WAD page: ")

# make sure we're actually on /idgames first
if not re.search("www.doomworld.com/idgames", wadurl) :
    print "ERROR: Not an /idgames page"
    quit()

# don't overwrite an existing directory called "temp"
if os.path.exists(startdir+"/temp") :
    print "ERROR: folder temp already exists"
    quit()

# create and enter temp directory
print "Creating working directory temp..."
os.system("mkdir temp")
print "Entering temp..."
os.chdir(startdir+"/temp")
directory = os.getcwd()

try :
    # Parse the WAD page
    wadpage = urllib2.urlopen(wadurl).read()
    soup = BeautifulSoup(wadpage, "html.parser")

    # Find and parse the table with the download links
    downloads = soup.find("table", class_="download")
    links = downloads.find_all("a", href=True)

    # Get the actual URLs out of the links
    for link in links :
        if re.search("\.zip$", link["href"].lower()) :
            wadlink.append(link["href"])
            lcount += 1
    if len(wadlink) == 0 :
        print "ERROR: No download links found."
        quit()

    # Actually download the thing
    print "Trying download from "+wadlink[0]+":"
    urllib.urlretrieve(wadlink[0], "newwad.zip", reporthook=dlProgress)
    pbar.finish()

    # Extract the name we will use for the WAD
    split = re.split("/([a-zA-Z0-9_-]{1,8})\.zip$", wadlink[0].lower())
    wadname = split[1]
    print "\nUsing name " + wadname +"."

    print "Unzipping..."
    os.system("unzip newwad.zip")
    print

    for filename in os.listdir(directory) :
        # Get rid of the zip file, we don't need it anymore
        if re.search("newwad\.zip$", filename.lower()) :
            os.system("rm " + filename)
            continue
        old_path = "%s/%s" % (directory, filename)
        new_filename = filename.lower()

        # If file doesn't already start with wadname, append it so we can keep 
        # everything together
        if not re.search("^"+wadname, new_filename) :
            new_filename = wadname + "_" + new_filename
        new_filename = new_filename.replace(" ", "")    # remove whitespace
        new_path = "%s/%s" % (directory, new_filename)
        os.rename(old_path, new_path)

        # Move files into correct directories
        print "Moving " + new_filename + "..."
        if re.search("\.txt", new_filename) :
            os.system("mv -i "+new_filename+" ../txt")
        else :
            os.system("mv -i "+new_filename+" ..")
except :
    print "Error:", sys.exc_info()[0]
    print "Fail. Aborting..."
    os.chdir(startdir)
    if os.path.exists("./temp") :
        os.system("rm -R temp")
    quit()

print "Removing temporary directory..."
os.chdir("..")
os.system("rm -R temp")

print "\n\nDone! Enjoy playing " + wadname + "."

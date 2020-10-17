import feedparser
from io import StringIO
from html.parser import HTMLParser
from os import path, makedirs
import re
import requests
import datetime
from urllib.parse import urlparse

def main():
  try:
    # Check to see if downloads directory exists
    downloadsPath = 'downloads'
    downloadsDirExists = path.exists(downloadsPath) and path.isdir(downloadsPath)

    # if not, create downloads directory
    if not downloadsDirExists:
      print('  the "%s" folder doesnt exist. Creating it now ... ' % downloadsPath)
      makedirs(downloadsPath)

    # Sample feed URLs
    # http://podcastfeeds.nbcnews.com/drone/api/query/audio/podcast/1.0/MSNBC-MADDOW-NETCAST-MP3.xml
    # http://joeroganexp.joerogan.libsynpro.com/rss

    # Get the feed URL
    feed = input("Enter the feed xml url (e.g. http://podcastdomain.com/path/to/file.xml): ")

    # Check if feed is vaild URL
    parsedUrl = urlparse(feed)

    # Check to see if parsedUrl.scheme, parsedUrl.netloc and parsedUrl.path have values
    if parsedUrl.scheme == "" or parsedUrl.netloc == "" or parsedUrl.path == "":
      # if not, throw an exception
      raise Exception("Invalid URL: %s" % feed)

    print('  parsing URL ...', end = '')
    # Parse the feed URL
    NewsFeed = feedparser.parse(feed)
    print('done')

    # Check to see Channel and Title exist
    print('  Confirming valid title ...', end = '')
    if type(NewsFeed) is not dict or not NewsFeed.has_key('channel'):
      # if not, throw an exception
      raise Exception("Invalid channel or title")
    print('done')

    # Get the Channel Title
    channelTitle = NewsFeed['channel']['title']
    channelTitlePath = downloadsPath + "/" + channelTitle

    print('  checking if podcast directory exists ...')
    # Check to see if Channel Title directory exists under downloads directory
    channelTitleDirExists = path.exists(channelTitlePath) and path.isdir(channelTitlePath)

    # if not, create Channel Title directory under downloads directory
    if not channelTitleDirExists:
      print('  the channel folder "%s" doesnt exist. Creating it now ... ' % channelTitlePath, end = '')
      makedirs(channelTitlePath)

    print('done')

    # Download the MP3 files
    for x in NewsFeed.entries:
      titleDateObj = datetime.datetime.strptime(x.published, '%a, %d %b %Y %H:%M:%S %z')
      filename = channelTitlePath + "/" + str(titleDateObj.date()) + " - " + x.title + ".mp3"
      print('  downloading filename: %s ... ' % filename, end = '')
      r = requests.get(x.links[0].href, allow_redirects=True)
      open(filename, 'wb').write(r.content)
      print('done')
  except Exception as error:
    print("Error: %s" % error)

if __name__ == "__main__":
  main()
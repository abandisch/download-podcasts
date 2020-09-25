import feedparser
from io import StringIO
from html.parser import HTMLParser
from os import path, makedirs
import re
import requests
import datetime

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()

def main():
  try:
    # Check to see if downloads directory exists
    downloadsPath = 'downloads'
    downloadsDirExists = path.exists(downloadsPath) and path.isdir(downloadsPath)

    # if not, create downloads directory
    if not downloadsDirExists:
      print('  the "%s" folder doesnt exist. Creating it now ... ' % downloadsPath)
      makedirs(downloadsPath)

    # Get the feed URL
    feed = "http://podcastfeeds.nbcnews.com/drone/api/query/audio/podcast/1.0/MSNBC-MADDOW-NETCAST-MP3.xml"
    # feed = "http://joeroganexp.joerogan.libsynpro.com/rss"
    # feed = input("Enter the feed xml url: ")

    # Parse the feed URL
    NewsFeed = feedparser.parse(feed)

    # Get the Channel Title
    channelTitle = NewsFeed['channel']['title']
    channelTitlePath = downloadsPath + "/" + channelTitle

    # Check to see if Channel Title directory exists under downloads directory
    channelTitleDirExists = path.exists(channelTitlePath) and path.isdir(channelTitlePath)

    # if not, create Channel Title directory under downloads directory
    if not channelTitleDirExists:
      print('  the channel folder "%s" doesnt exist. Creating it now ... ' % channelTitlePath)
      makedirs(channelTitlePath)


    # entry = NewsFeed.entries[1]

    # entry.summary - entry.title .mp3
    # "August 21 2020 - Bannon legal woes leave Trump scrambling for distance (again).mp3"

    # # print('NewsFeed.entries[1]: %s ' % NewsFeed.entries[1])
    # print('NewsFeed.entries[1].title: %s ' % NewsFeed.entries[1].title)
    # print('NewsFeed.entries[1].published: %s ' % NewsFeed.entries[1].published)
    # titleDateObj = datetime.datetime.strptime(NewsFeed.entries[1].published, '%a, %d %b %Y %H:%M:%S %z')
    # print('titleDate: %s ' % titleDateObj.date())

    for x in NewsFeed.entries:
      # s = MLStripper()
      # s.feed(x.summary)
      # titleDate = re.sub('[^0-9a-zA-Z]+', '-', s.get_data())
      titleDateObj = datetime.datetime.strptime(x.published, '%a, %d %b %Y %H:%M:%S %z')
      filename = channelTitlePath + "/" + str(titleDateObj.date()) + " - " + x.title + ".mp3"
      print('downloading filename: %s' % filename)
      r = requests.get(x.links[0].href, allow_redirects=True)
      open(filename, 'wb').write(r.content)
      print('done')
  except Exception as error:
    print("Error: %s" % error)

if __name__ == "__main__":
  main()
import feedparser
from io import StringIO
from html.parser import HTMLParser
import re
import requests

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
    # feed = "http://podcastfeeds.nbcnews.com/drone/api/query/audio/podcast/1.0/MSNBC-MADDOW-NETCAST-MP3.xml"
    feed = input("Enter the feed xml url: ")
    NewsFeed = feedparser.parse(feed)

    entry = NewsFeed.entries[1]

    # entry.summary - entry.title .mp3
    # "August 21 2020 - Bannon legal woes leave Trump scrambling for distance (again).mp3"

    for x in NewsFeed.entries:
      s = MLStripper()
      s.feed(x.summary)
      titleDate = re.sub('[^0-9a-zA-Z]+', '-', s.get_data())
      # print('link: %s' % x.links[0].href)
      # print('date: %s' % titleDate)
      # print('title: %s' % x.title)
      # print('value: %s' % x.summary_detail.value)
      filename = titleDate + " - " + x.title + ".mp3"

      print('downloading filename: %s' % filename)
      r = requests.get(x.links[0].href, allow_redirects=True)
      open(filename, 'wb').write(r.content)
      print('done')
  except Exception as error:
    print("Error: %s" % error)

if __name__ == "__main__":
  main()
import feedparser
import shutil
import podcastparser
from io import StringIO
from html.parser import HTMLParser
import urllib
from os import path, makedirs
import re
import requests
import datetime
from urllib.parse import urlparse
import pprint
# from json import load, loads


def get_ending(linkname):
  if linkname:
    split_link = linkname.split(".")
    ending = split_link[-1]
    print('ENDING FOUND', ending)
    return (ending, split_link)
    # get last el of the string

def download_file(url, filename):
  with requests.get(url, stream=True) as r:
        with open(filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
  return True

def check_if_file_is_audio_link(poss_link):
  if poss_link:
    # NOTE derived from https://en.wikipedia.org/wiki/Audio_file_format
    audio_formats = ["3gp", "aac", "act", "aiff", "alac", "amr", "flac", "m4a", "m4b", "mp3", "mp4", "mpc", "mogg", "oga", "ogg", "tta", "wav", "wv"]
    formatted = get_ending(poss_link)
    ending = formatted[0]

    # TODO use regex to check for the items above? this doesn't work of there's a tracking query string at the end of the url
    raw_url = formatted[1]

    for format in audio_formats:
      if ending == format:
        return ending
    
    return None
      

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
    # feed = "http://joeroganexp.joerogan.libsynpro.com/rss"
    title = input('Enter the Podcast name: ')
    feed = input("Enter the feed xml url (e.g. http://podcastdomain.com/path/to/file.xml and not feed:http://): ")

    # TODO restore this Check if feed is vaild URL
    # parsedUrl = urlparse(feed)

    # Check to see if parsedUrl.scheme, parsedUrl.netloc and parsedUrl.path have values
    # if parsedUrl.scheme == "" or parsedUrl.netloc == "" or parsedUrl.path == "":
    #   # if not, throw an exception
    #   raise Exception("Invalid URL: %s parsed is %s scheme is %s netloc is %s path is %s" % (feed, parsedUrl, parsedUrl.scheme, parsedUrl.netloc, parsedUrl.path))

    print('  parsing URL ...', end = '')
    # Parse the feed URL
    # ProtoNewsFeed = feedparser.parse('feed:' + feed)
    # NewsFeed = ProtoNewsFeed['feed']

    # NOTE FEED should be http and not feed:http
    parsedFromParser = podcastparser.parse(feed, urllib.request.urlopen(feed))
  

      # NewsFeed = feedparser.parse(feed)
  
    # print('done &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&', )

    # Check to see Channel and Title exist
    # print('  Confirming valid title ...', end = '')
    # if title.__len__ == 0:
    #   if type(NewsFeed) is not dict or not NewsFeed.has_key('channel'):
    #     # if not, throw an exception
    #     raise Exception("Invalid channel or title", NewsFeed)
    #   else:
    #     title = NewsFeed['channel']['title']
    

    # Get the Channel Title
    channelTitlePath = downloadsPath + "/" + title

    print('  checking if podcast directory exists ...')
    # Check to see if Channel Title directory exists under downloads directory
    channelTitleDirExists = path.exists(channelTitlePath) and path.isdir(channelTitlePath)

    # if not, create Channel Title directory under downloads directory
    if not channelTitleDirExists:
      print('  the channel folder "%s" doesnt exist. Creating it now ... ' % channelTitlePath, end = '')
      makedirs(channelTitlePath)

    print('done')

    try:
      ep_count = 1
      pp = pprint.PrettyPrinter(indent=4)
      if parsedFromParser:
        for ep in parsedFromParser["episodes"]:
          print("~~~~~~~~~~~~~~~~~~~~~~~~~~~EP~~~~~~~~~~~~~~~~~~~~~~",pp.pprint(ep.get("enclosures", 'No Enclosures Found')))
          possible_enclosures = ep.get("enclosures", None)
          # TODO we should get the extension of the file of the url and use it rather than manually setting mp3
          
          if ep["title"]:
            filename = ep["title"] #+ ".mp3"
          elif parsedFromParser["description"]:
            filename = parsedFromParser["description"] + '-{}'.format(ep_count) #".mp3"
          else:
            filename = " %d " % (ep_count)

          if possible_enclosures:
            list_of_enclosures = ep["enclosures"]
            last_enclosure = ''
            for enclosure in list_of_enclosures:
              maybe_url = enclosure.get('url', None)
              if maybe_url != last_enclosure:
                ending = check_if_file_is_audio_link(maybe_url)
                if ending:
                  link = maybe_url
                download_file(link, channelTitlePath + "/" + filename + "." + ending)
                last_enclosure = maybe_url
          

          # TODO For next time, sanitize file names
          # TODO handle erroring out when link doesn't end in an audio file extension


          # titleDateObj = datetime.datetime.strptime(x.published, '%a, %d %b %Y %H:%M:%S %z')
          # filename = channelTitlePath + "/" + str(titleDateObj.date()) + " - " + x.title + ".mp3"
          # print('  downloading filename: %s ... ' % filename, end = '')
          # r = requests.get(x.links[0].href, allow_redirects=True)
          # open(filename, 'wb').write(r.content)
          ep_count = ep_count + 1
          print('done')
          # TODO handle if parsedfromparser doesn't exist
    except Exception as error:
      print('Nested Exception parsedFromParser error', error, 'parsedFromParser', pprint.pformat(parsedFromParser, indent=2, sort_dicts=True))

    # Download the MP3 files
    # try:
    #   for x in NewsFeed.entries:
    #     titleDateObj = datetime.datetime.strptime(x.published, '%a, %d %b %Y %H:%M:%S %z')
    #     filename = channelTitlePath + "/" + str(titleDateObj.date()) + " - " + x.title + ".mp3"
    #     print('  downloading filename: %s ... ' % filename, end = '')
    #     r = requests.get(x.links[0].href, allow_redirects=True)
    #     open(filename, 'wb').write(r.content)
    #     print('done')
    # except Exception as error:
    #   print('Nested Exception newsfeed error', error, 'NewsFeed', NewsFeed)

  except Exception as error:
    print("Error:", error, parsedFromParser, 'catch')

if __name__ == "__main__":
  main()
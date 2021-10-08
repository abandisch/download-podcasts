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

def remove_feed_from_url(url):
  if url:
    conv_url = str(url)
    # TODO this could easily be cleaner with regex

    check_for_feed = conv_url[0:4].lower()
    print("FEED", check_for_feed)
    if check_for_feed == 'feed':
      new_url = url[5:]
      print('NEW URL', new_url)
      return new_url
    else:
      return url

    
    

def get_ending(linkname):
  if linkname:
    # Handle cases with a query string ie. pod.com/somefile.mp3?=someotherquery
    sanitize_link = linkname.split('/')
    # print('SANITY LINK', sanitize_link)
    sanitized_link = sanitize_link[-1]
    # print('SED~~~~~~~~~~~~~', sanitized_link)
    split_link = sanitized_link.split(".")
    ending = split_link[-1]
    q_mark_found = ending.find("?")
    if q_mark_found != -1:
      remove_querystring = ending.split("?")
      sanitized_ending = remove_querystring[0]
      # print("SANITIZED ENDING FOUND", sanitized_ending)
      return sanitized_ending
    # print('ENDING FOUND', ending)
    return ending
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
    ending = get_ending(poss_link)
    # TODO it would be nice to use regex to check for the items but this doesn't work? 
    # poss_audio = re.search("\b(3gp|aac|act|aiff|alac|amr|flac|m4a|m4b|mp3|mp4|mpc|mogg|oga|ogg|tta|wav|wv)\w*\b", ending)
    # print('AUDDDOOOO', poss_audio, ending)
    
    for format in audio_formats:
      if ending == format:
        return ending
    
    return None

# TODO This would be good as a class and series of functions within the class
# TODO This would be wonderful as an installable CLI app.

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

    removed_feed = remove_feed_from_url(feed)

    # TODO restore this Check if feed is vaild URL
    # parsedUrl = urlparse(feed)

    # Check to see if parsedUrl.scheme, parsedUrl.netloc and parsedUrl.path have values
    # if parsedUrl.scheme == "" or parsedUrl.netloc == "" or parsedUrl.path == "":
    #   # if not, throw an exception
    #   raise Exception("Invalid URL: %s parsed is %s scheme is %s netloc is %s path is %s" % (feed, parsedUrl, parsedUrl.scheme, parsedUrl.netloc, parsedUrl.path))

    # print('  parsing URL ...', end = '')
    # Parse the feed URL
    # ProtoNewsFeed = feedparser.parse('feed:' + feed)
    # NewsFeed = ProtoNewsFeed['feed']

    parsedFromParser = podcastparser.parse(removed_feed, urllib.request.urlopen(removed_feed))

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
          # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~EP~~~~~~~~~~~~~~~~~~~~~~",pp.pprint(ep.get("enclosures", 'No Enclosures Found')))
          possible_enclosures = ep.get("enclosures", None)
          
          if ep["title"]:
            filename = ep["title"]
          elif parsedFromParser["description"]:
            filename = parsedFromParser["description"] + '-{}'.format(ep_count)
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
          

          # TODO For next time, sanitize file names removing /
          # TODO handle erroring out when link doesn't end in an audio file extension


          # TODO Get the date and time of publication and if it exists, add it to the
          # titleDateObj = datetime.datetime.strptime(x.published, '%a, %d %b %Y %H:%M:%S %z')
          # filename = channelTitlePath + "/" + str(titleDateObj.date()) + " - " + x.title + ".mp3"
          # print('  downloading filename: %s ... ' % filename, end = '')
          # r = requests.get(x.links[0].href, allow_redirects=True)
          # open(filename, 'wb').write(r.content)
          ep_count = ep_count + 1
          print('done')
    except Exception as error:
      print('Nested Exception parsedFromParser error', error, 'parsedFromParser', pprint.pformat(parsedFromParser, indent=2, sort_dicts=True))


  except Exception as error:
    print("Error:", error, parsedFromParser, 'catch')

if __name__ == "__main__":
  main()
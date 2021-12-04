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


# TODO This would be wonderful as an installable CLI app.
class RssFeed():
  def __init__(self, downloads_path = "downloads"):
    self.downloads_path = downloads_path

  def main(self):
    try:
      # Check to see if downloads directory exists
      
      downloadsDirExists = path.exists(self.downloads_path) and path.isdir(self.downloads_path)

      # if not, create downloads directory
      if not downloadsDirExists:
        print('  the "%s" folder doesnt exist. Creating it now ... ' % self.downloads_path)
        makedirs(self.downloads_path)

      # Sample feed URLs
      # http://podcastfeeds.nbcnews.com/drone/api/query/audio/podcast/1.0/MSNBC-MADDOW-NETCAST-MP3.xml
      # http://joeroganexp.joerogan.libsynpro.com/rss

      # Get the feed URL
      # feed = "http://joeroganexp.joerogan.libsynpro.com/rss"
      title = input('Enter the Podcast name: ')
      feed = input("Enter the feed xml url (e.g. http://podcastdomain.com/path/to/file.xml and not feed:http://): ")

      removed_feed = self.__remove_feed_from_url(feed)

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
      channelTitlePath = self.downloads_path + "/" + title

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
              found_filename = ep["title"]
            elif parsedFromParser["description"]:
              found_filename = parsedFromParser["description"] + '-{}'.format(ep_count)
            else:
              found_filename = " %d " % (ep_count)
            
            filename = self.__sanitize_filename(found_filename)
            print('FILENAME', filename)
            if possible_enclosures:
              list_of_enclosures = ep["enclosures"]
              last_enclosure = ''
              for enclosure in list_of_enclosures:
                maybe_url = enclosure.get('url', None)
                if maybe_url != last_enclosure:
                  ending = self.__check_if_file_is_audio_link(maybe_url)
                  if ending:
                    link = maybe_url
                    self.__download_file(link, channelTitlePath + "/" + filename + "." + ending)
                  last_enclosure = maybe_url
            

            


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
  
  # NOTE PRIVATE METHODS BELOW

  def __check_if_file_is_audio_link(self, poss_link):
    if poss_link:
      # NOTE list derived from https://en.wikipedia.org/wiki/Audio_file_format
      audio_formats = ["3gp", "aac", "act", "aiff", "alac", "amr", "flac", "m4a", "m4b", "mp3", "mp4", "mpc", "mogg", "oga", "ogg", "tta", "wav", "wv"]
      valid_extensions_regex = ""
      for ext in audio_formats:
        valid_extensions_regex = valid_extensions_regex + "\." + str(ext) + "$|"
      
      valid_extensions_regex = valid_extensions_regex[:-1]

      # NOTE should return boolean.
      return bool(re.search(valid_extensions_regex, poss_link, flags=re.IGNORECASE))
  
  def __download_file(self, url, filename):
    with requests.get(url, stream=True) as r:
          with open(filename, 'wb') as f:
              shutil.copyfileobj(r.raw, f)
    return True
  
  # def __get_ending(self, linkname):
  #   if linkname:
  #     # Handle cases with a query string ie. pod.com/somefile.mp3?=someotherquery
  #     sanitize_link = linkname.split('/')
  #     # print('SANITY LINK', sanitize_link)
  #     sanitized_link = sanitize_link[-1]
  #     # print('SED~~~~~~~~~~~~~', sanitized_link)
  #     split_link = sanitized_link.split(".")
  #     ending = split_link[-1]
  #     q_mark_found = ending.find("?")
  #     if q_mark_found != -1:
  #       remove_querystring = ending.split("?")
  #       sanitized_ending = remove_querystring[0]
  #       # print("SANITIZED ENDING FOUND", sanitized_ending)
  #       return sanitized_ending
  #     # print('ENDING FOUND', ending)
  #     return ending
  
  def __remove_feed_from_url(self, url):
    if url:
      try:
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
      except Exception as error:
        print('[RssFeed].__remove_feed_from_url - error', error)
        raise Exception(error)
  
  def __sanitize_filename(self, filename):
    if filename:
      try:
        orig_filename = str(filename)
        first_name= re.sub(r'[\'!;,:"\\/]', '', orig_filename, flags=re.IGNORECASE)
        updated_filename = re.sub('\.(?=.*\.)', '', first_name, flags=re.IGNORECASE)
        
        return updated_filename

      except Exception as error:
        # print('[RssFeed].__sanitize_filename', error)
        raise Exception('[RssFeed].__sanitize_filename' + error)
    else:
      raise Exception('[RssFeed].__sanitize_filename - filename not found')


if __name__ == "__main__":
  new_path = "downthemall"
  rss = RssFeed(new_path)
  # rss = RssFeed()
  rss.main()

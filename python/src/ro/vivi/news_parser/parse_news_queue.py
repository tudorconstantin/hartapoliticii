# -*- coding: utf-8 -*-

'''
Created on Nov 17, 2012

Fetches the list of links that have been submitted by users to the site. Crawls
their content and spits it out in XML form for the entity_extractor to go over
and identify people in it.

note: get dict2xml from https://github.com/quandyfactory/dict2xml

@author okvivi

'''

import urllib, urllib2, os
import sys, time
import dict2xml
import re,codecs

from bs4 import BeautifulSoup
from HTMLParser import HTMLParseError

from ro.vivi.news_parser.crawler import *

NO_CACHE = False


def get_content_for_url(link):
  data = get_news_html('./python/src/ro/vivi/news_parser/news_queue', link)

  data = replace_circ_diacritics(data)
  data = replace_html_comments(data)

  try:
    soup = BeautifulSoup(data, "lxml")
  except HTMLParseError:
    return 'error'

  title = soup.html.head.title.contents

  print "--"
  print title

  return str(soup.html.body.contents), ''.join(title[0])


WORK_DIR = 'python/src/ro/vivi/news_parser/news_queue'
if len(sys.argv) > 1:
  WORK_DIR = sys.argv[1]

try:
  f = urllib2.urlopen('http://zen.dev/api/get_unmoderated_news_queue.php')
except IOError, e:
  print "Error: ", e
  sys.exit(1)

all_xml = ''

lines = f.read().split("\n")

for line in lines:
  if line == '':
    continue

  time_ms, link = line.split(' ')
  content, title = get_content_for_url(link)

  new_item = {
        'news_source' : 'ugc',
        'news_link' : link,
        'news_title': title,
        'news_time':   time.strftime("%H %M %d %m %Y",
                                     time.localtime(float(time_ms))),
        'news_content': urllib.quote(content),
        'news_status' : 'fresh',
        'news_place' : '',
      }
  xml = dict2xml.dict2xml(new_item)
  xml = re.sub(' type="\w+"', '',
               xml.replace('<?xml version="1.0" encoding="UTF-8" ?>', ''))
  xml = xml.replace('root>', 'item>')
  all_xml += "<item>\n" + xml + "</item>\n\n"


time.strftime("%Y%m%d-%H")
all_xml_fname = WORK_DIR + '/daily_%s.txt' % time.strftime("%Y%m%d-%H")
f = codecs.open(all_xml_fname, "w", "utf-8")
f.write("<all>\n" + all_xml + "\n</all>")
f.close

print "\ndone."
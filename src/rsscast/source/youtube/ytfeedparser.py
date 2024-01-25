# MIT License
#
# Copyright (c) 2021 Arkadiusz Netczuk <dev.arnet@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import os
import logging

# import pprint

import requests
import requests_file

import feedparser

from rsscast.rss.rsschannel import RSSChannel, get_channel_output_dir
from rsscast.utils import write_text


_LOGGER = logging.getLogger(__name__)


## ============================================================


def parse_rss( feedId, feedUrl, write_content=True ) -> RSSChannel:
    status, feedContent = read_url( feedUrl )
    if status == 404:
        _LOGGER.error("unable to get url content: %s", feedUrl)
        return None

    _LOGGER.info( "feed %s: reading url %s status code: %s", feedId, feedUrl, status )
    channelPath = get_channel_output_dir( feedId )
    sourceRSS = os.path.abspath( os.path.join(channelPath, "source.rss") )
    if write_content:
        write_text( feedContent, sourceRSS )
    _LOGGER.info( "feed %s: parsing rss", feedId )
    rssChannel = RSSChannel()
    if not parse_rss_content(rssChannel, feedContent ):
        # unable to parse
        _LOGGER.warning( "feed[%s]: unable to parse RSS %s", feedId, sourceRSS )
        return None
    _LOGGER.info( "feed %s: parsing done", feedId )
    return rssChannel


def parse_rss_content(rss_channel: RSSChannel, feedContent):
    parsedDict = feedparser.parse( feedContent )
    if parsedDict.get('bozo', False):
        reason = parsedDict.get('bozo_exception', "<unknown>")
        _LOGGER.warning( "channel[%s]: malformed rss detected, reason %s\n", rss_channel.title, reason )
        return False

    parsedDict = feedparser.parse( feedContent )
    # pprint.pprint( parsedDict )
    return rss_channel.parseData(parsedDict)


def read_url( urlpath ):
    session = requests.Session()
    session.mount( 'file://', requests_file.FileAdapter() )
#     session.config['keep_alive'] = False
#     response = requests.get( urlpath, timeout=5 )
    response = session.get( urlpath, timeout=5 )
#     response = requests.get( urlpath, timeout=5, hooks={'response': print_url} )
    return response.status_code, response.text

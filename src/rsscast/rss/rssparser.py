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
from typing import List
from functools import cmp_to_key

# import pprint

import html
import requests
import requests_file
import feedparser

from rsscast import DATA_DIR, persist


_LOGGER = logging.getLogger(__name__)


## ============================================================


FEED_SUBDIR = "feed"


class RSSItem( persist.Versionable ):
    """Single RSS item in channel."""

    ## 0 - first version
    ## 1 - added 'enabled' field
    ## 2 - added 'mediaSize' field
    _class_version = 2

    def __init__(self, itemId=None, link=None):
        self.id = itemId
        self.link = link
        self.title = None
        self.summary = None
        self.publishDate = None
        self.mediaSize = -1                 ## in bytes

        ## thumbnail
        self.thumb_url    = None
        self.thumb_width  = None
        self.thumb_height = None

        self.enabled = True

    def _convertstate_( self, dict_, dictVersion_ ):
        _LOGGER.info( "converting object from version %s to %s", dictVersion_, self._class_version )

        if dictVersion_ is None:
            dictVersion_ = -1

        dictVersion_ = max(dictVersion_, 0)

        if dictVersion_ == 0:
            dict_["enabled"] = True
            dictVersion_ = 1

        if dictVersion_ == 1:
            dict_["mediaSize"] = -1
            dictVersion_ = 2

        # pylint: disable=W0201
        self.__dict__ = dict_

    def videoId(self):
        return self.id.replace(":", "_")

    # returns public URL to resource
    def getExternalURL(self, host, feedId):
        videoId = self.videoId()
        return f"http://{host}/{FEED_SUBDIR}/{feedId}/{videoId}.mp3"             ## must have absolute path

    def itemTitle(self):
        return html.escape( self.title )

    def localFileSize(self):
        if self.mediaSize < 0:
            return None
        return self.mediaSize

    def switchEnabled(self):
        self.enabled = not self.enabled


class RSSChannel( persist.Versionable ):
    """RSS data structure representing channel's RSS with list of items"""

    ## 0 - first version
    _class_version = 0

    def __init__(self):
        self.title                   = None
        self.link                    = None
        self.publishDate             = None
        self.items: List[ RSSItem ]  = []

    def _convertstate_( self, dict_, dictVersion_ ):
        _LOGGER.info( "converting object from version %s to %s", dictVersion_, self._class_version )

        if dictVersion_ is None:
            dictVersion_ = -1

        dictVersion_ = max(dictVersion_, 0)

        # pylint: disable=W0201
        self.__dict__ = dict_

    def size(self):
        return len( self.items )

    def get(self, index) -> RSSItem:
        return self.items[ index ]

#     def getList(self) -> List[  RSSItem ]:
#         return self.items

    def getItemsURLs(self):
        return { item.link for item in self.items }

    def addItem(self, rssItem: RSSItem):
        found = self.findItemById( rssItem.id )
        if found is not None:
            return False
        self.items.append( rssItem )
        self._sortItems()
        return True

    def removeItem(self, rssItem: RSSItem):
        self.items.remove( rssItem )

    def itemIndex(self, rssItem: RSSItem) -> int:
        return self.items.index( rssItem )

    def findItemById(self, itemId) -> RSSItem:
        for item in self.items:
            if item.id == itemId:
                return item
        return None

    def update(self, channel: "RSSChannel"):
        self.title = channel.title
        self.link  = channel.link
        self.publishDate = channel.publishDate
        for item in channel.items:
            self.addItem( item )
        self._sortItems()

    def parse(self, feedContent):
        parsedDict = feedparser.parse( feedContent )
        if parsedDict.get('bozo', False):
            reason = parsedDict.get('bozo_exception', "<unknown>")
            _LOGGER.warning( "malformed rss detected, reason %s", reason )
            return False

        parsedDict = feedparser.parse( feedContent )
        # pprint.pprint( parsedDict )
        return self.parseData(parsedDict)

    def parseData(self, parsedDict):
        """ Parse data dict.

        Expects following dict:
        {
            "feed": {
                "title": string
                "href": string
                "published": string, in format '2014-05-24T20:50:40+00:00'
            }
            "entries": [ {
                    "id": string
                    "title": string
                    "link": string
                    "media_thumbnail": [ {
                            "url": string
                            "width": string
                            "height": string
                        }
                    ]
                    "summary": string
                    "published": string, in format '2020-06-14T13:45:00+00:00'
                }
            ]
        }
        """
        parsedFeed = parsedDict['feed']
        self.title = parsedFeed['title']
        self.link = parsedFeed.get('href', "")
        self.publishDate = parsedFeed.get('published', "")

        for post in parsedDict.get('entries', []):
    #         pprint( post )

            rssItem = RSSItem()

            rssItem.id = post['id']
    #         rssItem.id = post['yt_videoid']

            rssItem.link = post['link']
            rssItem.title = post['title']

            if 'media_thumbnail' in post:
                thumbnail = post['media_thumbnail'][0]
                rssItem.thumb_url    = thumbnail['url']
                width = thumbnail.get('width')
                if width:
                    rssItem.thumb_width = width
                height = thumbnail.get('height')
                if height:
                    rssItem.thumb_height = height

            rssItem.summary = post.get('summary', '')
            rssItem.publishDate = post['published']

#             linkSize = get_media_size( rssItem.link, False )
#             if linkSize != None:
#                 rssItem.mediaSize = linkSize

            self.addItem( rssItem )

        return True

    def _sortItems( self ):
#         def sort_key( rssItem: RSSItem ):
#             return rssItem.publishDate

        def cmp_none( obj1, obj2 ):
            if obj2 is None:
                if obj1 is None:
                    ## both None
                    return 0
                return -1
            if obj1 is None:
                return 1
            ## none objects None
            return -2

        def compare( rssItem1: RSSItem, rssItem2: RSSItem ):
            rss_none = cmp_none( rssItem1, rssItem2 )
            if rss_none > -2:
                ## one or two None
                return rss_none

            pub_none = cmp_none( rssItem1.publishDate, rssItem2.publishDate )
            if pub_none > -2:
                ## one or two None
                return pub_none

            if rssItem1.publishDate < rssItem2.publishDate:
                return -1
            if rssItem1.publishDate > rssItem2.publishDate:
                return 1
            return 0

        self.items.sort( key=cmp_to_key(compare) )


## ============================================================


def parse_rss( feedId, feedUrl, write_content=True ) -> RSSChannel:
    _LOGGER.info( "feed %s: reading url %s", feedId, feedUrl )
    feedContent = read_url( feedUrl )
    if write_content:
        channelPath = get_channel_output_dir( feedId )
        sourceRSS = os.path.abspath( os.path.join(channelPath, "source.rss") )
        write_text( feedContent, sourceRSS )
    _LOGGER.info( "feed %s: parsing rss", feedId )
    rssChannel = RSSChannel()
    if not rssChannel.parse( feedContent ):
        # unable to parse
        return None
    _LOGGER.info( "feed %s: parsing done", feedId )
    return rssChannel


def read_url( urlpath ):
    session = requests.Session()
    session.mount( 'file://', requests_file.FileAdapter() )
#     session.config['keep_alive'] = False
#     response = requests.get( urlpath, timeout=5 )
    response = session.get( urlpath, timeout=5 )
#     response = requests.get( urlpath, timeout=5, hooks={'response': print_url} )
    return response.text


def get_channel_output_dir( feed_dir_name ):
    channelPath = os.path.abspath( os.path.join(DATA_DIR, FEED_SUBDIR, feed_dir_name) )
    os.makedirs( channelPath, exist_ok=True )
    return channelPath


def write_text( content, outputPath ):
    with open( outputPath, 'wt', encoding="utf-8" ) as fp:
        fp.write( content )

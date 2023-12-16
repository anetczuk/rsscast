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

import logging
import glob
import os
import re
from typing import List
from collections import Counter

from rsscast import persist
from rsscast.rss.rssparser import RSSChannel, RSSItem, get_channel_output_dir
from rsscast.rss.rssconverter import generate_channel_rss, remove_item_data
from rsscast.rss.ytparser import parse_url


_LOGGER = logging.getLogger(__name__)


class FeedEntry( persist.Versionable ):
    """RSS channel wrapped in form of entry in channels list"""

    ## 0 - first version
    ## 1 - add 'enabled' field
    ## 2 - add 'channel' field
    _class_version = 2

    def __init__(self):
        self.feedName            = None            ## defined by user
        self.feedId              = None            ## defined by user
        self.url                 = None
        self.channel: RSSChannel = RSSChannel()
        self.enabled             = True

    def _convertstate_( self, dict_, dictVersion_ ):
        _LOGGER.info( "converting object from version %s to %s", dictVersion_, self._class_version )

        if dictVersion_ is None:
            dictVersion_ = -1

        dictVersion_ = max(dictVersion_, 0)

        if dictVersion_ == 0:
            dict_["enabled"] = True
            dictVersion_ = 1

        if dictVersion_ == 1:
            dict_["channel"] = RSSChannel()
            dictVersion_ = 2

        # pylint: disable=W0201
        self.__dict__ = dict_

    def countItems(self):
        return self.channel.size()

    def update(self, channel: RSSChannel):
        if self.channel is None:
            self.channel = channel
            return
        if channel is None:
            return
        self.channel.update( channel )

    def updateFromContent(self, feedContent):
        rssChannel = RSSChannel()
        rssChannel.parse( feedContent )
        self.update( rssChannel )

    def updateLocalData(self):
        """Read media size from files stored locally"""

        if self.channel is None:
            return
        feedId = self.feedId.replace(":", "_")
        feedId = re.sub( r"\s+", "", feedId )

        channelPath = get_channel_output_dir( feedId )

        for rssItem in self.channel.items:
            videoId = rssItem.videoId()
            postLocalPath = f"{channelPath}/{videoId}.mp3"

            if os.path.exists(postLocalPath):
                rssItem.mediaSize = os.path.getsize( postLocalPath )
            else:
                rssItem.mediaSize = -1

    def fixRepeatedTitles( self ):
        if self.channel is None:
            return
        titleCounter = Counter()
        for rssItem in self.channel.items:
            titleCounter.update( [rssItem.title] )
            counted = titleCounter[ rssItem.title ]
            if counted > 1:
                rssItem.title += " [R" + str(counted) + "]"

    def addItem(self, rssItem: RSSItem):
        if self.channel is None:
            return
        self.channel.addItem(rssItem)

    def removeItem(self, rssItem: RSSItem):
        if self.channel is None:
            return
        self.channel.removeItem( rssItem )
        remove_item_data( self.feedId, rssItem )

    def printData(self) -> str:
        return str( self.feedName ) + " " + str( self.feedId ) + " " + str( self.url ) + " " + str( self.enabled )


def fetch_feed( feed: FeedEntry ):
    """Download channel's source RSS."""
    feedId = feed.feedId
    rssChannel: RSSChannel = None
    if feed.countItems() < 1:
        # empty list
        rssChannel = parse_url( feedId, feed.url, full_list=True )
    else:
        rssChannel = parse_url( feedId, feed.url )
    feed.update( rssChannel )
    feed.updateLocalData()
    feed.fixRepeatedTitles()


def parse_feed( feed: FeedEntry ):
    """Fetch media and generate converted RSS."""
    try:
        fetch_feed( feed )
        generate_channel_rss( feed.feedId, feed.channel )
    except Exception as ex:
        _LOGGER.exception( "unable parse feed: %s reaseon: %s", feed.feedId, ex, exc_info=False )
        raise


## ========================================================


class FeedContainer( persist.Versionable ):
    """RSS channels list"""

    ## 0 - first version
    _class_version = 0

    def __init__(self):
        self.feedList: List[  FeedEntry ] = []

    def _convertstate_( self, dict_, dictVersion_ ):
        _LOGGER.info( "converting object from version %s to %s", dictVersion_, self._class_version )

        if dictVersion_ is None:
            dictVersion_ = -1

        dictVersion_ = max(dictVersion_, 0)

#         if dictVersion_ == 0:
#             dict_["stockList"] = dict()
#             dictVersion_ = 1

        # pylint: disable=W0201
        self.__dict__ = dict_

    def size(self):
        return len( self.feedList )

    def get(self, index):
        return self.feedList[ index ]

    def getList(self) -> List[  FeedEntry ]:
        return self.feedList

    def countItems(self):
        count = 0
        for item in self.feedList:
            count += item.countItems()
        return count

    def addFeedNew(self, feedName: str, feedId: str, feedUrl: str):
        feed = FeedEntry()
        feed.feedName = feedName
        feed.feedId = feedId
        feed.url = feedUrl
        self.feedList.append( feed )

    def addFeed(self, feed: FeedEntry):
        self.feedList.append( feed )

    def replaceFeed( self, oldFeed: FeedEntry, newFeed: FeedEntry ):
        _LOGGER.debug( "replacing feed %s with %s", oldFeed, newFeed )
        for i, _ in enumerate( self.feedList ):
            currItem = self.feedList[i]
            if currItem == oldFeed:
                self.feedList[i] = newFeed
#                 self.sort()
                return True
        _LOGGER.debug( "replacing failed" )
        return False

    def removeFeed(self, feed):
        self.feedList.remove( feed )


class UserContainer():
    """Application's user data container"""

    ## 0 - first version
    ## 1 - feed container
    _class_version = 1

    def __init__(self):
        self.notes = { "notes": "" }        ## default notes
        self.feed  = FeedContainer()

    def store( self, outputDir ):
        changed = False

        outputFile = outputDir + "/version.obj"
        if persist.store_object( self._class_version, outputFile ) is True:
            changed = True

        outputFile = outputDir + "/notes.obj"
        if persist.store_object( self.notes, outputFile ) is True:
            changed = True

        outputFile = outputDir + "/feed.obj"
        if persist.store_object( self.feed, outputFile ) is True:
            changed = True

        ## backup data
        objFiles = glob.glob( outputDir + "/*.obj" )
        storedZipFile = outputDir + "/data.zip"
        persist.backup_files( objFiles, storedZipFile )

        return changed

    def load( self, inputDir ):
        inputFile = inputDir + "/version.obj"
        mngrVersion = persist.load_object( inputFile, self._class_version )
        if mngrVersion != self. _class_version:
            _LOGGER.info( "converting object from version %s to %s", mngrVersion, self._class_version )
            ## do nothing for now

        inputFile = inputDir + "/notes.obj"
        self.notes = persist.load_object( inputFile, self._class_version )
        if self.notes is None:
            self.notes = { "notes": "" }

        inputFile = inputDir + "/feed.obj"
        self.feed = persist.load_object( inputFile, self._class_version )
        if self.feed is None:
            self.feed = FeedContainer()

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
from typing import List

from rsscast import persist
from rsscast.rss.rssparser import parse_rss, RSSChannel
from rsscast.rss.rssconverter import generate_content


_LOGGER = logging.getLogger(__name__)


class FeedEntry( persist.Versionable ):

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
            dictVersion_ = 0

        if dictVersion_ < 0:
            ## nothing to do
            dictVersion_ = 0

        if dictVersion_ == 0:
            dict_["enabled"] = True
            dictVersion_ = 1

        if dictVersion_ == 1:
            dict_["channel"] = RSSChannel()
            dictVersion_ = 2

        # pylint: disable=W0201
        self.__dict__ = dict_

    def update(self, channel: RSSChannel):
        if self.channel is None:
            self.channel = channel
            return
        self.channel.update( channel )

    def printData(self) -> str:
        return str( self.feedName ) + " " + str( self.feedId ) + " " + str( self.url ) + " " + str( self.enabled )


def fetch_feed( feed: FeedEntry ):
    feedId = feed.feedId
    rssChannel: RSSChannel = parse_rss( feedId, feed.url )
    feed.update( rssChannel )    


def pull_feed( hostIp, feed: FeedEntry ):
    feedId = feed.feedId
    generate_content( hostIp, feedId, feed.channel )
    

def parse_feed( hostIp, feed: FeedEntry ):
    fetch_feed( feed )
    pull_feed( hostIp, feed )
    
#     ## old
#     convert_rss( hostIp, feed.feedId, feed.url )


## ========================================================


class FeedContainer( persist.Versionable ):

    ## 0 - first version
    _class_version = 0

    def __init__(self):
        self.feedList: List[  FeedEntry ] = []

    def _convertstate_( self, dict_, dictVersion_ ):
        _LOGGER.info( "converting object from version %s to %s", dictVersion_, self._class_version )

        if dictVersion_ is None:
            dictVersion_ = 0

        if dictVersion_ < 0:
            ## nothing to do
            dictVersion_ = 0

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

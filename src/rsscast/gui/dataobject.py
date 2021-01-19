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
from typing import Dict, List
import glob

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QWidget, QUndoStack

from rsscast import persist
# from rsscast.dataaccess.gpw.gpwdata import GpwIndicatorsData
# from rsscast.dataaccess.dividendsdata import DividendsCalendarData
# from rsscast.dataaccess.finreportscalendardata import PublishedFinRepsCalendarData, FinRepsCalendarData
# from rsscast.dataaccess.globalindexesdata import GlobalIndexesData
# from rsscast.dataaccess.gpw.gpwcurrentdata import GpwCurrentStockData,\
#     GpwCurrentIndexesData
#
# import rsscast.gui.threadlist as threadlist
# from rsscast.gui.command.addfavgroupcommand import AddFavGroupCommand
# from rsscast.gui.command.deletefavgroupcommand import DeleteFavGroupCommand
# from rsscast.gui.command.renamefavgroupcommand import RenameFavGroupCommand
# from rsscast.gui.command.addfavcommand import AddFavCommand
# from rsscast.gui.command.deletefavcommand import DeleteFavCommand
# from rsscast.gui.command.reorderfavgroupscommand import ReorderFavGroupsCommand
# from rsscast.gui.datatypes import UserContainer, StockData,\
#     GpwStockIntradayMap, GpwIndexIntradayMap, FavData, WalletData,\
#     broker_commission, TransHistory, TransactionMatchMode
# from rsscast.dataaccess.gpw.gpwespidata import GpwESPIData


_LOGGER = logging.getLogger(__name__)


class FeedEntry():

    def __init__(self):
        self.feedName = None
        self.feedId   = None
        self.url      = None


class FeedContainer( persist.Versionable ):

    ## 0 - first version
    _class_version = 0

    def __init__(self):
        self.feedList: List[  FeedEntry ] = []

    def _convertstate_(self, dict_, dictVersion_ ):
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

    def addFeed(self, feedName: str, feedId: str, feedUrl: str):
        feed = FeedEntry()
        feed.feedName = feedName
        feed.feedId = feedId
        feed.url = feedUrl
        self.feedList.append( feed )


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


## ====================================================================


class DataObject( QObject ):

    feedChanged = pyqtSignal()

    def __init__(self, parent: QWidget=None):
        super().__init__( parent )
        self.parentWidget = parent

        self.userContainer      = UserContainer()                   ## user data

        self.undoStack = QUndoStack(self)

#         self.favsChanged.connect( self.updateAllFavsGroup )

    def store( self, outputDir ):
        return self.userContainer.store( outputDir )

    def load( self, inputDir ):
        self.userContainer.load( inputDir )

    @property
    def notes(self) -> Dict[str, str]:
        return self.userContainer.notes

    @notes.setter
    def notes(self, newData: Dict[str, str]):
        self.userContainer.notes = newData

    @property
    def feed(self) -> FeedContainer:
        return self.userContainer.feed

    def addFeed(self, feedName: str, feedId: str, feedUrl: str):
        self.userContainer.feed.addFeed( feedName, feedId, feedUrl )
        self.feedChanged.emit()

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
from typing import Dict

from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QWidget, QUndoStack

from rsscast.gui.widget.feeddialog import FeedDialog
from rsscast.gui.command.addentrycommand import AddEntryCommand
from rsscast.gui.datatypes import UserContainer, FeedContainer
from rsscast.gui.command.editentrycommand import EditEntryCommand
from rsscast.gui.command.removeentrycommand import RemoveEntryCommand
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
        self.feedChanged.emit()

    @property
    def notes(self) -> Dict[str, str]:
        return self.userContainer.notes

    @notes.setter
    def notes(self, newData: Dict[str, str]):
        self.userContainer.notes = newData

    @property
    def feed(self) -> FeedContainer:
        return self.userContainer.feed

    def pushUndo(self, undoCommand):
        self.undoStack.push( undoCommand )

    ## ================================================================

    def addEntry(self, feedName: str, feedId: str, feedUrl: str):
        self.userContainer.feed.addFeedNew( feedName, feedId, feedUrl )
        self.feedChanged.emit()

    def addEntryNew(self):
        parentWidget = self.parent()
        entryDialog = FeedDialog( None, parentWidget )
        entryDialog.setModal( True )
        dialogCode = entryDialog.exec_()
        if dialogCode == QtWidgets.QDialog.Rejected:
            return
        _LOGGER.debug( "adding entry: %s", entryDialog.entry.printData() )
        command = AddEntryCommand( self, entryDialog.entry )
        self.pushUndo( command )

    def editEntry(self, entry):
        if entry is None:
            return
        parentWidget = self.parent()
        entryDialog = FeedDialog( entry, parentWidget )
        entryDialog.setModal( True )
        dialogCode = entryDialog.exec_()
        if dialogCode == QtWidgets.QDialog.Rejected:
            return
        command = EditEntryCommand( self, entry, entryDialog.entry )
        self.pushUndo( command )

    def removeEntry(self, entry):
        if entry is None:
            return
        command = RemoveEntryCommand( self, entry )
        self.pushUndo( command )

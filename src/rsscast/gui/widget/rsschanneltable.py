# MIT License
#
# Copyright (c) 2020 Arkadiusz Netczuk <dev.arnet@gmail.com>
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
from datetime import datetime, time, timedelta

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QAbstractTableModel
from PyQt5.QtWidgets import QTableView
from PyQt5.QtGui import QColor

from rsscast.rss.rssparser import RSSChannel, RSSItem
from rsscast.gui import guistate


_LOGGER = logging.getLogger(__name__)


class RSSChannelTableModel( QAbstractTableModel ):

    def __init__(self, data: RSSChannel):
        super().__init__()
        self._rawData: RSSChannel = data

    # pylint: disable=R0201
    def getItem(self, itemIndex: QModelIndex):
        if itemIndex.isValid():
            return itemIndex.internalPointer()
        return None

    def setContent(self, data: RSSChannel):
        self.beginResetModel()
        self._rawData = data
        self.endResetModel()

    # pylint: disable=W0613
    def rowCount(self, parent=None):
        if self._rawData is None:
            return 0
        return self._rawData.size()

    # pylint: disable=W0613
    def columnCount(self, parnet=None):
        attrsList = self.attributeLabels()
        return len( attrsList )

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            attrsList = self.attributeLabels()
            return attrsList[ section ]
        return super().headerData( section, orientation, role )

    ## for invalid parent return elements form root list
    def index(self, row, column, parent: QModelIndex):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        entry = self._rawData.get( row )
        return self.createIndex(row, column, entry)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            entry = self._rawData.get( index.row() )
            rawData = self.attribute( entry, index.column() )
            if rawData is None:
                return "-"
            if isinstance(rawData, time):
                return rawData.strftime("%H:%M")
            if isinstance(rawData, timedelta):
                return print_timedelta( rawData )
            if isinstance(rawData, datetime):
                return rawData.strftime("%Y-%m-%d %H:%M")
            return rawData
            ### converting to str() abuses ordering/sorting of numeric values
#             strData = str(rawData)
#             return strData

        if role == Qt.UserRole:
            entry = self._rawData.get( index.row() )
            rawData = self.attribute( entry, index.column() )
            return rawData

        if role == Qt.EditRole:
            entry = self._rawData.get( index.row() )
            rawData = self.attribute( entry, index.column() )
            return rawData

        if role == Qt.BackgroundRole:
            entry: RSSItem = self._rawData.get( index.row() )
            if entry.enabled is False:
                return QColor( "gray" )

#         if role == Qt.TextAlignmentRole:
#             if index.column() == 4:
#                 return Qt.AlignLeft | Qt.AlignVCenter
#             return Qt.AlignHCenter | Qt.AlignVCenter

        return None

    def getIndex(self, item, parentIndex: QModelIndex=None, column: int = 0):
        if parentIndex is None:
            parentIndex = QModelIndex()
        if parentIndex.isValid():
            # dataTask = parentIndex.data( Qt.UserRole )
            dataTask = parentIndex.internalPointer()
            if dataTask == item:
                return parentIndex
        elems = self.rowCount( parentIndex )
        for i in range(elems):
            index = self.index( i, column, parentIndex )
            if index.isValid() is False:
                continue
            # dataTask = parentIndex.data( Qt.UserRole )
            dataTask = index.internalPointer()
            if dataTask == item:
                return index
        return None

    def attribute(self, entry: RSSItem, index):
        if index == 0:
            modelIndex = self.getIndex( entry )
            row = modelIndex.row()
            return row + 1
        elif index == 1:
            return entry.title
        elif index == 2:
            return entry.id
        elif index == 3:
            return entry.link
        return None

    @staticmethod
    def attributeLabels():
        return ( "#", "Title", "Id", "URL" )


## ===========================================================


class RSSChannelTable( QTableView ):

    selectedItem    = pyqtSignal( RSSItem )
    itemUnselected  = pyqtSignal()

    def __init__(self, parentWidget=None):
        super().__init__(parentWidget)
        self.setObjectName("rsschanneltable")

        self.dataObject: RSSChannel = None

        self.setSortingEnabled( True )
        self.setShowGrid( False )
        self.setAlternatingRowColors( True )
#         self.setEditTriggers( QAbstractItemView.DoubleClicked )

        header = self.horizontalHeader()
        header.setDefaultAlignment( Qt.AlignCenter )
        header.setHighlightSections( False )
        header.setStretchLastSection( True )

        self.verticalHeader().hide()

        self.dataModel = RSSChannelTableModel( None )
        self.proxyModel = QtCore.QSortFilterProxyModel(self)
        self.proxyModel.setSourceModel( self.dataModel )
        self.setModel( self.proxyModel )

    def loadSettings(self, settings):
        wkey = guistate.get_widget_key(self, "tablesettings")
        settings.beginGroup( wkey )
        visDict = settings.value("columnsVisible", None, type=dict)
        if visDict is None:
            visDict = dict()

    def saveSettings(self, settings):
        wkey = guistate.get_widget_key(self, "tablesettings")
        settings.beginGroup( wkey )
        settings.setValue("columnsVisible", self.columnsVisible )
        settings.endGroup()

    ## ===============================================

    def connectData(self, channel: RSSChannel ):
        self.dataObject = channel
        self.refreshData()

    def refreshData(self):
        self.dataModel.setContent( self.dataObject )
        self.clearSelection()
#         _LOGGER.debug( "entries: %s\n%s", type(history), history.printData() )

    def refreshEntry(self, entry: RSSItem=None):
        if entry is None:
            ## unable to refresh entry row -- refresh whole model
            self.refreshData()
            return
        taskIndex = self.getIndex( entry )
        if taskIndex is None:
            ## unable to refresh entry row -- refresh whole model
            self.refreshData()
            return
        lastColIndex = taskIndex.sibling( taskIndex.row(), 4 )
        if lastColIndex is None:
            ## unable to refresh entry row -- refresh whole model
            self.refreshData()
            return
        self.proxyModel.dataChanged.emit( taskIndex, lastColIndex )

    def getIndex(self, entry: RSSItem, column: int = 0):
        modelIndex = self.dataModel.getIndex( entry, column=column )
        if modelIndex is None:
            return None
        proxyIndex = self.proxyModel.mapFromSource( modelIndex )
        return proxyIndex

    def getItem(self, itemIndex: QModelIndex ) -> RSSItem:
        sourceIndex = self.proxyModel.mapToSource( itemIndex )
        return self.dataModel.getItem( sourceIndex )

    def contextMenuEvent( self, event ):
        evPos          = event.pos()
        entry: RSSItem = None
        mIndex = self.indexAt( evPos )
        if mIndex is not None:
            entry = self.getItem( mIndex )
 
#         create_entry_contextmenu( self, self.dataObject, entry )
 
        contextMenu      = QtWidgets.QMenu( self )
        enableAction     = None
        if entry is None or entry.enabled is False:
            enableAction = contextMenu.addAction("Enable")
        else:
            enableAction = contextMenu.addAction("Disable")
 
        if entry is None:
            enableAction.setEnabled( False )
 
        globalPos = QtGui.QCursor.pos()
        action = contextMenu.exec_( globalPos )
 
        if action == enableAction:
            entry.switchEnabled()

    def currentChanged(self, current, previous):
        super().currentChanged( current, previous )
        item = self.getItem( current )
        if item is not None:
            self.selectedItem.emit( item )
        else:
            self.itemUnselected.emit()

#     def mouseDoubleClickEvent( self, event ):
#         evPos          = event.pos()
#         entry: RSSItem = None
#         mIndex = self.indexAt( evPos )
#         if mIndex is not None:
#             entry = self.getItem( mIndex )
# 
#         if entry is None:
#             self._addEntry()
#         else:
#             self._editEntry(entry)
# 
#         return super().mouseDoubleClickEvent(event)


def print_timedelta( value: timedelta ):
    s = ""
    secs = value.seconds
    days = value.days
    if secs != 0 or days == 0:
        mm, _ = divmod(secs, 60)
        hh, mm = divmod(mm, 60)
        s = "%d:%02d" % (hh, mm)
#         s = "%d:%02d:%02d" % (hh, mm, ss)
    if days:
        def plural(n):
            return n, abs(n) != 1 and "s" or ""
        if s != "":
            s = ("%d day%s, " % plural(days)) + s
        else:
            s = ("%d day%s" % plural(days)) + s
#     micros = value.microseconds
#     if micros:
#         s = s + ".%06d" % micros
    return s

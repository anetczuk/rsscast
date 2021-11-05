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

from rsscast.datatypes import FeedEntry

from rsscast.gui import uiloader
from rsscast.gui.dataobject import DataObject


UiTargetClass, QtBaseClass = uiloader.load_ui_from_class_name( __file__ )


_LOGGER = logging.getLogger(__name__)


class FeedWidget( QtBaseClass ):           # type: ignore

    def __init__(self, parentWidget=None):
        super().__init__(parentWidget)
        self.ui = UiTargetClass()
        self.ui.setupUi(self)

        self.ui.feedTableView.selectedItem.connect( self._feedSelected )
        self.ui.feedTableView.itemUnselected.connect( self._feedUnselected )

    def connectData(self, dataObject: DataObject):
        self.ui.feedTableView.connectData( dataObject )

    def refreshView(self):
        self.ui.feedTableView.refreshData()
        self.ui.feedItemsView.refreshData()

    def _feedSelected(self, feed: FeedEntry):
#         print( "selected:", feed.feedName )
        dataObject = self.ui.feedTableView.dataObject
        self.ui.feedItemsView.connectData( dataObject, feed )

    def _feedUnselected(self):
#         print( "unselected" )
        self.ui.feedItemsView.clear()

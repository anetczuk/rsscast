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
import copy

from rsscast.gui.datatypes import FeedEntry

from .. import uiloader


UiTargetClass, QtBaseClass = uiloader.load_ui_from_class_name( __file__ )


_LOGGER = logging.getLogger(__name__)


class FeedDialog( QtBaseClass ):           # type: ignore

    def __init__(self, entry: FeedEntry, parentWidget=None):
        super().__init__(parentWidget)
        self.ui = UiTargetClass()
        self.ui.setupUi(self)

        self.entry: FeedEntry = None

        self.finished.connect( self._done )

        self.setObject( entry )

    def setObject(self, entry: FeedEntry):
        if entry is not None:
            self.entry = copy.deepcopy( entry )
        else:
            self.entry = FeedEntry()

        self.ui.nameLE.setText( self.entry.feedName )
        self.ui.idLE.setText( self.entry.feedId )
        self.ui.urlLE.setText( self.entry.url )

#         self.adjustSize()

    def _done(self, _):
        self.entry.feedName = self.ui.nameLE.text()
        self.entry.feedId = self.ui.idLE.text()
        self.entry.url = self.ui.urlLE.text()

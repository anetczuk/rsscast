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

from PyQt5.QtWidgets import QUndoCommand

from rsscast.datatypes import FeedContainer


_LOGGER = logging.getLogger(__name__)


class SetEnableStateEntryCommand( QUndoCommand ):

    def __init__(self, dataObject, entry, parentCommand=None):
        super().__init__(parentCommand)

        self.data = dataObject
        self.feedContainer: FeedContainer = self.data.feed
        self.entry = entry
        self.currentState = entry.enabled

        self.setText( "Switch Entry Enable State: " + str(entry.feedName) )

    def redo(self):
        self.entry.enabled = not self.currentState
        self.data.feedChanged.emit()

    def undo(self):
        self.entry.enabled = self.currentState
        self.data.feedChanged.emit()

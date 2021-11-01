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

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal

from rsscast import DATA_DIR
from rsscast.gui.dataobject import DataObject
from rsscast.rss.rssserver import RSSServerManager

from rsscast.gui import uiloader


UiTargetClass, QtBaseClass = uiloader.load_ui_from_class_name( __file__ )


_LOGGER = logging.getLogger(__name__)


class ServerWidget( QtBaseClass ):           # type: ignore

    _internalStatusChanged = pyqtSignal()
    statusChanged          = pyqtSignal()

    def __init__(self, parentWidget=None):
        super().__init__(parentWidget)
        self.ui = UiTargetClass()
        self.ui.setupUi(self)

        self.server = RSSServerManager()
        self.server.startedCallback = self._serverStarted
        self.server.stoppedCallback = self._serverStopped

        self.ui.portSB.setValue( RSSServerManager.DEFAULT_PORT )
        self.ui.startPB.clicked.connect( self.startServer )
        self.ui.stopPB.clicked.connect( self.stopServer )

        self._internalStatusChanged.connect( self.statusChanged, QtCore.Qt.QueuedConnection )
        self.statusChanged.connect( self.refreshWidget )

        self.refreshWidget()

    def connectData(self, dataObject: DataObject):
        ## do nothing
        pass

    def isServerStarted(self):
        status: RSSServerManager.Status = self.server.getStatus()
        if status is RSSServerManager.Status.STARTED:
            return True
        return False

    def startServer(self):
        self.server.port = self.ui.portSB.value()
        self.server.start( DATA_DIR )
        self.refreshWidget()

    def stopServer(self):
        self.server.stop()
        self.refreshWidget()

    def refreshWidget(self):
        status: RSSServerManager.Status = self.server.getStatus()
        self.ui.statusLabel.setText( status.value )
        if self.isServerStarted():
            self.ui.startPB.setEnabled( False )
            self.ui.stopPB.setEnabled( True )
        else:
            self.ui.startPB.setEnabled( True )
            self.ui.stopPB.setEnabled( False )

    def _serverStarted(self):
        self._internalStatusChanged.emit()

    def _serverStopped(self):
        self._internalStatusChanged.emit()

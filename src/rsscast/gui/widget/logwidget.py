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

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from rsscast.logger import get_logging_output_file
from rsscast.gui.appwindow import AppWindow

from .. import uiloader


UiTargetClass, QtBaseClass = uiloader.load_ui_from_class_name( __file__ )


_LOGGER = logging.getLogger(__name__)


class LogWidget( QtBaseClass ):           # type: ignore

    fileChanged   = pyqtSignal()

    def __init__(self, parentWidget=None):
        super().__init__(parentWidget)
        self.ui = UiTargetClass()
        self.ui.setupUi(self)

        self.fileChanged.connect( self._fileChanged, QtCore.Qt.QueuedConnection )
        self.ui.autoScrollCB.stateChanged.connect( self._autoScrollChanged )
        self.ui.autoScrollCB.setChecked( True )

#         self.ui.textEdit.textChanged.connect( self._textChanged )

        verticalBar = self.ui.textEdit.verticalScrollBar()
        verticalBar.rangeChanged.connect( self._scrollRangeChanged )
        verticalBar.valueChanged.connect( self._scrollValueChanged )

        self.logFile = get_logging_output_file()

        ## prevents infinite feedback loop
        logging.getLogger('watchdog.observers.inotify_buffer').setLevel(logging.INFO)

        event_handler = PatternMatchingEventHandler( patterns=[self.logFile] )
        event_handler.on_any_event = self._logFileCallback

        dirPath = os.path.dirname( self.logFile )
        self.observer = Observer()
        self.observer.schedule( event_handler, path=dirPath, recursive=False )        
      
        self.updateLogView()
        self.observer.start()

    def updateLogView(self):
        ## method can be run from different threads
        ## call method through Qt event queue to prevent
        ## concurrent access control
        QtCore.QTimer.singleShot( 1, self._updateText )
            
    def scrollDown(self):
        verticalBar = self.ui.textEdit.verticalScrollBar()
        verticalBar.triggerAction( QtWidgets.QAbstractSlider.SliderToMaximum )
    
    def _updateText(self):
        verticalBar = self.ui.textEdit.verticalScrollBar()
        currPos = verticalBar.value()
#         print( "_updateText", "val:", currPos )
        
        with open(self.logFile, "r") as myfile:
            fileText = myfile.read()
            self.ui.textEdit.setPlainText( str(fileText) )
            
        if self.ui.autoScrollCB.isChecked() == False:
            verticalBar.setValue( currPos )

    def _autoScrollChanged(self):
        if self.ui.autoScrollCB.isChecked():
            verticalBar = self.ui.textEdit.verticalScrollBar()
            verticalBar.setEnabled( False )
            self.scrollDown()
        else:
            verticalBar = self.ui.textEdit.verticalScrollBar()
            verticalBar.setEnabled( True )

#     def _textChanged(self):
#         verticalBar = self.ui.textEdit.verticalScrollBar()
#         print( "_textChanged", "val:", verticalBar.value() )

    def _scrollRangeChanged(self, minVal, maxVal):
        verticalBar = self.ui.textEdit.verticalScrollBar()
#         print( "_scrollRangeChanged", "min:", minVal, "max:", maxVal, "val:", verticalBar.value() )
        if self.ui.autoScrollCB.isChecked():
            verticalBar.setValue( maxVal )

    def _scrollValueChanged(self, value):
        verticalBar = self.ui.textEdit.verticalScrollBar()
#         print( "_scrollValueChanged", "val:", value, "max:", verticalBar.maximum() )
        if self.ui.autoScrollCB.isChecked():
            if value != verticalBar.maximum():
                verticalBar.setValue( verticalBar.maximum() )

    # Override closeEvent, to intercept the window closing event
    def closeEvent(self, event):
        self.observer.stop()
        self.observer.join()
        self.observer = None
        super().closeEvent( event )
        self.close()

    def _logFileCallback(self, _):
        if self.observer is None:
            ## window closed -- ignore
            return
        self.fileChanged.emit()

    def _fileChanged(self):
        self.updateLogView()


def create_window( parent=None ):
    logWindow = AppWindow( parent )
    newTitle = AppWindow.appTitle + " Log"
    logWindow.setWindowTitle( newTitle )
        
    widget = LogWidget( logWindow )
    logWindow.addWidget( widget )
    logWindow.move( 0, 0 )

    deskRec = QApplication.desktop().screenGeometry()
    deskWidth = deskRec.width()
    logWindow.resize( deskWidth, 600 )
    logWindow.show()
    return logWindow

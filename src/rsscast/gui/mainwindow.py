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
# import datetime
from typing import List

from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import qApp

from rsscast.datatypes import FeedEntry, parse_feed, fetch_feed

from rsscast.gui import threadlist
from rsscast.gui import uiloader
from rsscast.gui import trayicon
from rsscast.gui import guistate
from rsscast.gui.dataobject import DataObject
from rsscast.gui.appwindow import AppWindow
from rsscast.gui.widget import logwidget
from rsscast.gui.trayicon import load_main_icon, load_disconnect_icon
from rsscast.gui.resources import get_settings, get_user_data_path
from rsscast.gui.widget.settingsdialog import SettingsDialog, AppSettings


_LOGGER = logging.getLogger(__name__)


UiTargetClass, QtBaseClass = uiloader.load_ui_from_module_path( __file__ )


class MainWindow( QtBaseClass ):           # type: ignore

    logger: logging.Logger = None

    # pylint: disable=R0915
    def __init__(self):
        super().__init__()
        self.ui = UiTargetClass()
        self.ui.setupUi(self)

        self.data = DataObject( self )
        self.appSettings = AppSettings()

        self.refreshAction = QtWidgets.QAction(self)
        self.refreshAction.setShortcuts( QtGui.QKeySequence.Refresh )
        self.refreshAction.triggered.connect( self.pullDataForce )
        self.addAction( self.refreshAction )

        ## =============================================================

        undoStack = self.data.undoStack

        undoAction = undoStack.createUndoAction( self, "&Undo" )
        undoAction.setShortcuts( QtGui.QKeySequence.Undo )
        redoAction = undoStack.createRedoAction( self, "&Redo" )
        redoAction.setShortcuts( QtGui.QKeySequence.Redo )

        self.ui.menuEdit.insertAction( self.ui.actionUndo, undoAction )
        self.ui.menuEdit.removeAction( self.ui.actionUndo )
        self.ui.menuEdit.insertAction( self.ui.actionRedo, redoAction )
        self.ui.menuEdit.removeAction( self.ui.actionRedo )

        self.ui.actionSave_data.triggered.connect( self.saveData )
        self.ui.actionLogs.triggered.connect( self.openLogsWindow )
        self.ui.actionOptions.triggered.connect( self.openSettingsDialog )

        ## =============================================================

        self.trayIcon = trayicon.TrayIcon(self)
        self.setIconTheme( trayicon.TrayIconTheme.ORANGE )

        self.ui.serverWidget.connectData( self.data )
        self.ui.feedWidget.connectData( self.data )

        self.data.feedChanged.connect( self._updateFeedsNum )

        ## ================== connecting signals ==================

        self.ui.fetchRSSPB.clicked.connect( self.fetchRSS )
        self.ui.pullPB.clicked.connect( self.pullDataForce )

        self.ui.serverWidget.statusChanged.connect( self.updateTrayIndicator )
        self.ui.serverWidget.statusChanged.connect( self.updateTrayToolTip )
        self.ui.notesWidget.dataChanged.connect( self._handleNotesChange )

        #qApp.saveStateRequest.connect( self.saveSession )
        qApp.aboutToQuit.connect( self._handleAppQuit )

#         self.applySettings()
        self.trayIcon.show()

        self.setWindowTitle()

        self.setStatusMessage( "Ready", timeout=10000 )

    def loadData(self):
        """Load user related data (e.g. favs, notes)."""
        dataPath = get_user_data_path()
        self.data.load( dataPath )
        self.refreshView()

    def triggerSaveTimer(self):
        timeout = 30000
        _LOGGER.info("triggering save timer with timeout %s", timeout)
        QtCore.QTimer.singleShot( timeout, self.saveData )

    def saveData(self):
        if self._saveData():
            self.setStatusMessage( "Data saved" )
        else:
            self.setStatusMessage( "Nothing to save" )

    # pylint: disable=E0202
    def _saveData(self):
        ## having separate slot allows to monkey patch / mock "_saveData()" method
        _LOGGER.info( "storing data" )
        dataPath = get_user_data_path()
        self.data.notes = self.ui.notesWidget.getNotes()
        return self.data.store( dataPath )

    def disableSaving(self):
        def save_data_mock():
            _LOGGER.info("saving data is disabled")
        _LOGGER.info("disabling saving data")
        self._saveData = save_data_mock           # type: ignore

    def startServer(self):
        self.ui.serverWidget.startServer()

    def stopServer(self):
        self.ui.serverWidget.stopServer()

    ## ====================================================================

    def setWindowTitleSuffix( self, suffix="" ):
        if len(suffix) < 1:
            self.setWindowTitle( suffix )
            return
        newTitle = AppWindow.appTitle + " " + suffix
        self.setWindowTitle( newTitle )

    def setWindowTitle( self, newTitle="" ):
        if len(newTitle) < 1:
            newTitle = AppWindow.appTitle
        super().setWindowTitle( newTitle )
        self.updateTrayToolTip()

    def refreshView(self):
        self._updateFeedsNum()
        self.ui.serverWidget.refreshWidget()
        self.ui.feedWidget.refreshView()
        self.ui.notesWidget.setNotes( self.data.notes )

    def fetchRSS(self):
        function  = fetch_feed
        arguments = ()
        self._callOnFeeds(function, arguments, True)

    def pullDataForce(self):
        function  = parse_feed
        arguments = ()
        self._callOnFeeds(function, arguments)

    def _callOnFeeds(self, function, arguments, processDisabled=False):
        self._enableActions( False )

#         objects = self.findChildren( QtCore.QObject )
#         _LOGGER.info( 'Objects = %d' % len(objects) )

#         threads = threadlist.QThreadList( self )
#         threads = threadlist.SerialList( self )
        threads = threadlist.QThreadMeasuredList( self )
        threads.deleteOnFinish()
#         threads = threadlist.ProcessList( self )

        threads.finished.connect( self._refreshingFinished, Qt.QueuedConnection )

        feedList: List[ FeedEntry ] = self.data.feed.getList()
        feedList = sorted(feedList, key=lambda item: item.feedId if item else None)
        for feed in feedList:
            if processDisabled is False and feed.enabled is False:
                continue
            argsList = list( arguments )
            argsList.append( feed )
            args = tuple(argsList)
            threads.appendFunction( function, args )
        threads.start()

    def _refreshingFinished(self):
        self.ui.feedWidget.refreshView()
        self._updateFeedsNum()
        self._enableActions( True )

    def _enableActions(self, state=True):
        self.refreshAction.setEnabled( state )
        self.ui.pullPB.setEnabled( state )
        self.ui.fetchRSSPB.setEnabled( state )

    def _updateFeedsNum(self):
        itemsNum = self.data.feed.countItems()
        self.ui.itemsNum.setText( str(itemsNum) )

    ## ====================================================================

    def _handleNotesChange(self):
        self.triggerSaveTimer()

    ## ====================================================================

    def setStatusMessage(self, firstStatus, changeStatus: list = None, timeout=6000):
        if not changeStatus:
            changeStatus = [ firstStatus + " +", firstStatus + " =" ]
        statusBar = self.statusBar()
        message = statusBar.currentMessage()
        if message == firstStatus:
            statusBar.showMessage( changeStatus[0], timeout )
            return
        try:
            currIndex = changeStatus.index( message )
            nextIndex = ( currIndex + 1 ) % len(changeStatus)
            statusBar.showMessage( changeStatus[nextIndex], timeout )
        except ValueError:
            statusBar.showMessage( firstStatus, timeout )

    def updateTrayToolTip(self):
        if hasattr(self, 'trayIcon') is False:
            return
        toolTip = self.windowTitle()
        if self.ui.serverWidget.isServerStarted():
            toolTip += "\n" + "Server started"
            self.trayIcon.setToolTip( toolTip )
        else:
            toolTip += "\n" + "Server stopped"
            self.trayIcon.setToolTip( toolTip )

    def getIconTheme(self) -> trayicon.TrayIconTheme:
        return self.appSettings.trayIcon

    def setIconTheme(self, theme: trayicon.TrayIconTheme):
        _LOGGER.debug("setting tray theme: %r", theme)
        self.appSettings.trayIcon = theme
        appIcon = load_main_icon( theme )
        self.setWindowIcon( appIcon )
        self.updateTrayIndicator()

        ## update charts icon
#         chartIcon = load_chart_icon( theme )
#         widgets = self.findChildren( AppWindow )
#         for w in widgets:
#             w.setWindowIcon( chartIcon )

    def updateTrayIndicator(self):
        theme = self.appSettings.trayIcon
        if self.ui.serverWidget.isServerStarted():
            appIcon = load_main_icon( theme )
            self.trayIcon.setIcon( appIcon )
        else:
            appIcon = load_disconnect_icon( theme )
            self.trayIcon.setIcon( appIcon )

    def showEvent(self, _):
        self.trayIcon.updateLabel()

    def hideEvent(self, _):
        self.trayIcon.updateLabel()

    def setVisible(self, state):
        childrenWindows = self.findChildren( AppWindow )
        for w in childrenWindows:
            w.setVisible( state )
        super().setVisible( state )

    # Override closeEvent, to intercept the window closing event
    def closeEvent(self, event):
        _LOGGER.info("received close event, saving session: %s", qApp.isSavingSession() )
        if qApp.isSavingSession():
            ## closing application due to system shutdown
            self._handleOSShutdown()
            return
        ## windows close requested by user -- hide the window
        event.ignore()
        self.hide()
        self.trayIcon.show()

    ## ====================================================================

    def closeApplication(self):
        """Close application -- triggered from File->Exit menu."""
        _LOGGER.info("received exit request")
        qApp.quit()

    ## executes on "QApplication::quit()"
    def _handleAppQuit(self):
        """Handle successful quit of application.

        Received on 'QApplication::quit()' and on SIGINT signal.
        """
        _LOGGER.info( "received 'aboutToQuit()' signal")
        self.stopServer()

    def _handleOSShutdown(self):
        """Received 'close' event while OS shutting down."""
        self.saveAll()
        self.stopServer()

    def saveAll(self):
        _LOGGER.info("saving application state")
        self.saveSettings()
        self.saveData()

    ## ====================================================================

    def openLogsWindow(self):
        logwidget.create_window( self )

    def openSettingsDialog(self):
        dialog = SettingsDialog( self.appSettings, self )
        dialog.setModal( True )
        dialog.iconThemeChanged.connect( self.setIconTheme )
        dialogCode = dialog.exec_()
        if dialogCode == QDialog.Rejected:
            self.applySettings()
            return
        self.appSettings = dialog.appSettings
        self.applySettings()

    def applySettings(self):
        self.setIconTheme( self.appSettings.trayIcon )

    def loadSettings(self):
        """Load Qt related settings (e.g. layouts, sizes)."""
        settings = get_settings( self )
        self.logger.debug( "loading app state from %s", settings.fileName() )

        self.appSettings.loadSettings( settings )

        self.applySettings()

        ## restore widget state and geometry
        guistate.load_state( self, settings )

    def saveSettings(self):
        settings = get_settings( self )
        self.logger.debug( "saving app state to %s", settings.fileName() )

        self.appSettings.saveSettings( settings )

        ## store widget state and geometry
        guistate.save_state(self, settings)

        ## force save to file
        settings.sync()


MainWindow.logger = _LOGGER.getChild(MainWindow.__name__)

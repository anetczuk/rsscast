#!/usr/bin/python3
#
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

try:
    ## following import success only when file is directly executed from command line
    ## otherwise will throw exception when executing as parameter for "python -m"
    # pylint: disable=W0611
    import __init__
except ImportError:
    ## when import fails then it means that the script was executed indirectly
    ## in this case __init__ is already loaded
    pass

import sys
import logging
import argparse

from PyQt5.QtWidgets import QApplication

from rsscast import logger
from rsscast.gui.sigint import setup_interrupt_handling
from rsscast.gui.mainwindow import MainWindow


## ============================= main section ===================================


if __name__ != '__main__':
    sys.exit(0)


parser = argparse.ArgumentParser(description='RSS Cast Example')
parser.add_argument('-lud', '--loadUserData', action='store_const', const=True, default=False, help='Load user data' )
parser.add_argument('--minimized', action='store_const', const=True, default=False, help='Start minimized' )

args = parser.parse_args()


logFile = logger.get_logging_output_file()
logger.configure( logFile )

_LOGGER = logging.getLogger(__name__)


_LOGGER.debug( "Starting the application" )


app = QApplication(sys.argv)
app.setApplicationName("RSSCast")
app.setOrganizationName("arnet")
app.setQuitOnLastWindowClosed( False )

setup_interrupt_handling()

window = MainWindow()
window.setWindowTitleSuffix( "Preview" )
window.disableSaving()
window.setWindowTitle( window.windowTitle() )

if args.loadUserData:
    window.loadData()
else:
    window.data.addEntry( "Real Python", "realpython",
                          "http://www.youtube.com/feeds/videos.xml?channel_id=UCI0vQvr9aFn27yR6Ej6n5UA" )
    window.data.addEntry( "Monty Python", "montypython",
                          "http://www.youtube.com/feeds/videos.xml?user=MontyPython" )

window.loadSettings()
window.startServer()
window.refreshView()

window.show()
# if args.minimized is True or window.appSettings.startMinimized is True:
#     ## starting minimized
#     pass
# else:
#     window.show()

#window.openLogsWindow()

exitCode = app.exec_()

if exitCode == 0:
    window.saveSettings()

sys.exit( exitCode )

#!/usr/bin/python3
#
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

import sys

import argparse
import logging
from typing import List

from PyQt5.QtCore import QCoreApplication

import rsscast.logger as logger

from rsscast import DATA_DIR
from rsscast.rss.rssserver import RSSServerManager

from rsscast.datatypes import FeedEntry, parse_feed, fetch_feed
from rsscast.gui.resources import get_user_data_path
from rsscast.gui.dataobject import DataObject


_LOGGER = logging.getLogger(__name__)


class CliApp:

    def __init__(self):
        self.app  = None
        self.data: DataObject = None

    def init( self ):
        if self.app is None:
            self.app = QCoreApplication( sys.argv )
            set_app_data( self.app )

        if self.data is None:
            self.loadData()

    def loadData(self):
        self.data = DataObject()
        dataPath = get_user_data_path()
        self.data.load( dataPath )

    def saveData(self):
        if self.data is None:
            return
        dataPath = get_user_data_path()
        self.data.store( dataPath )

    def fetchRSS(self):
        feedList: List[ FeedEntry ] = self.data.feed.getList()
        for feed in feedList:
#             if feed.enabled is False:
#                 continue
            fetch_feed( feed )

    def refreshRSS(self):
        feedList: List[ FeedEntry ] = self.data.feed.getList()
        for feed in feedList:
            if feed.enabled is False:
                continue
            parse_feed( feed )

    def startServer(self):
        pass


def set_app_data( app ):
    app.setApplicationName("RSSCast")
    app.setOrganizationName("arnet")
    ### app.setOrganizationDomain("www.my-org.com")


def run_cli( args ):
    appData = CliApp()
    cli_mode = False

    if args.fetchRSS:
        cli_mode = True
        appData.init()
        _LOGGER.info( "fetching feed" )
        appData.fetchRSS()
        _LOGGER.info( "fetching done" )

    if args.refreshRSS:
        cli_mode = True
        appData.init()
        _LOGGER.info( "refreshing feed" )
        appData.refreshRSS()
        _LOGGER.info( "refreshing done" )

    if cli_mode:
        appData.saveData()

    if args.startServer:
        _LOGGER.info( "starting server" )
        cli_mode = True

        try:
            server = RSSServerManager()
            server.port = 8080
            server.execute( DATA_DIR )
        except KeyboardInterrupt:
            _LOGGER.info("stopping the server")

        _LOGGER.info( "server closed" )

    return cli_mode


def create_parser( parser: argparse.ArgumentParser = None ):
    if parser is None:
        parser = argparse.ArgumentParser(description='RSS Cast')
    parser.add_argument('--fetchRSS', action='store_const', const=True, default=False, help='Update RSS channels' )
    parser.add_argument('--refreshRSS', action='store_const', const=True, default=False,
                        help='Update RSS channels and download content' )
    parser.add_argument('--startServer', action='store_const', const=True, default=False, help='Start RSS server' )
    return parser


def main( args=None ):
    logger.configure()

    if args is None:
        parser = create_parser()
        args = parser.parse_args()

    _LOGGER.debug( "Starting the application" )
    _LOGGER.debug( "Logger log file: %s", logger.log_file )

    exitCode = 1

    try:
        exitCode = 0
        run_cli( args )

    except BaseException:
        _LOGGER.exception("Exception occurred")
        raise

    finally:
        sys.exit(exitCode)

    return exitCode


if __name__ == '__main__':
    main()

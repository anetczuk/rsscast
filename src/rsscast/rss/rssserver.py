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

# import feedparser
import os
import logging
import threading
from enum import Enum, unique
from typing import Callable

import socket
import socketserver
import urllib.parse
import posixpath

from http.server import SimpleHTTPRequestHandler

from rsscast.synchronized import synchronized


_LOGGER = logging.getLogger(__name__)


## implementation allows to pass custom base path
class RootedHTTPRequestHandler(SimpleHTTPRequestHandler):

    def translate_path(self, path):
        base_path = self.server.base_path
        if base_path is None:
            ## no base path given -- standard implementation
            return super().translate_path( path )

        path = posixpath.normpath(urllib.parse.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = base_path
        for word in words:
            _, word = os.path.splitdrive(word)
#             drive, word = os.path.splitdrive(word)
            _, word = os.path.split(word)
#             head, word = os.path.split(word)
            if word in (os.curdir, os.pardir):
                continue
            path = os.path.join(path, word)
        return path


## ======================================================


class RSSServer( socketserver.TCPServer ):

    def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True):
        super().__init__( server_address, RequestHandlerClass, bind_and_activate )
        self.base_path = None


## ======================================================


class RSSServerManager():

    @unique
    class Status(Enum):
        """Server status."""

        STARTED        = 'Started'
        STOPPED        = 'Stopped'

    DEFAULT_PORT = 8080
    Handler = RootedHTTPRequestHandler
#     Handler = SimpleHTTPRequestHandler

    def __init__(self):
        socketserver.TCPServer.allow_reuse_address = True
        self.port = RSSServerManager.DEFAULT_PORT
        self._service = None
        self._thread = None
        self._rootDir = None
        self.startedCallback: Callable = None
        self.stoppedCallback: Callable = None

    @staticmethod
    def getPrimaryIp():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0] + ":" + str(RSSServerManager.DEFAULT_PORT)
        except BaseException:
            IP = '127.0.0.1' + ":" + str(RSSServerManager.DEFAULT_PORT)
        finally:
            s.close()
        return IP

#         hostname = socket.gethostname()
#         local_ip = socket.gethostbyname(hostname)
#         return local_ip

#         return socket.gethostbyname( socket.getfqdn() )

    @synchronized
    def getStatus(self) -> 'RSSServerManager.Status':
        if self._service is not None:
            return RSSServerManager.Status.STARTED
        return RSSServerManager.Status.STOPPED

    # asynchronous call
    @synchronized
    def start(self, rootDir=None):
        if self._service is not None:
            ## already started
            return
        self._rootDir = rootDir
        self._thread = threading.Thread(target=self._run, args=())
        self._thread.start()

    @synchronized
    def stop(self):
        if self._service is None:
            ## not started
            return
        _LOGGER.info( "stopping feed server" )
        serverThread = self._thread     ## self._thread will be null-ed soon
        self._shutdownService()
        serverThread.join()

    ## busy execution
    @synchronized
    def execute(self, rootDir=None):
        self._rootDir = rootDir
        self._run()

    def _run(self):
        with RSSServer(("", self.port), RSSServerManager.Handler) as httpd:
#         with socketserver.TCPServer(("", self.port), RSSServerManager.Handler) as httpd:
            self._service = httpd
            self._service.base_path = self._rootDir
            try:
                _LOGGER.info("serving at port %s", self.port)
                httpd.allow_reuse_address = True
                self._notifyStarted()
                httpd.serve_forever()
    #             httpd.handle_request()
            finally:
                self._service.server_close()
                self._service = None
                self._thread = None
                self._notifyStopped()
        _LOGGER.info( "server thread ended" )

    @synchronized
    def _shutdownService(self):
        if self._service is None:
            return
        self._service.shutdown()

    def _notifyStarted(self):
        if not callable( self.startedCallback ):
            return
        # pylint: disable=E1102
        self.startedCallback()

    def _notifyStopped(self):
        if not callable( self.stoppedCallback ):
            return
        # pylint: disable=E1102
        self.stoppedCallback()

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
import logging
import threading

from feedgen.feed import FeedGenerator
import socketserver
from http.server import BaseHTTPRequestHandler

from rsscast.synchronized import synchronized
from rsscast.gui.dataobject import DataObject, FeedEntry
from typing import List
import requests
import requests_file


_LOGGER = logging.getLogger(__name__)


class RSSRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        _LOGGER.info( "request line: %s command: %s path: %s address: %s", self.requestline, self.command, self.path, self.address_string() )
        self._handlePath()

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        # Doesn't do anything with posted data
        self._handlePath()

    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
    ## =====================================================================

    def _handlePath( self ):
        #  os.path.splitext(path)
        if self.path == "/":
            self._listContent()
            return
        if self.path.startswith( "/feed/" ):
            subPath = self.path[ 6: ]
            self._feed( subPath )
            return
        
        self._respond404()

    def _listContent(self):
        _LOGGER.info( "listing table of content" )
        
        self._set_headers()
        
        entriesContent = ""
        feedList = self.getFeedList()
        if not feedList:
            entriesContent = "no entries"
        else:
            for feed in feedList:
                entriesContent += "<a href='feed/%s'>%s</a></br>" % ( feed.feedId, feed.feedName )

        content = f"""<html>
    <body>
{entriesContent}
    </body>
</html>
"""
        encoded = content.encode("utf8")                                # NOTE: must return a bytes object!
        self.wfile.write( encoded )
    
    def _feed(self, subPath):
        """This just generates an HTML document that includes `message`
        in the body. Override, or re-write this do do more interesting stuff.
        """
        
        feed = self.getFeed( subPath )
        if not feed:
            self._respond404()
            return
        
        _LOGGER.info( "generating feed for %s", feed.feedId )
        
        self._set_headers()

        _LOGGER.info( "reading %s", feed.url )
        session = requests.Session()
        session.mount( 'file://', requests_file.FileAdapter() )
#     session.config['keep_alive'] = False
#     response = requests.get( urlpath, timeout=5 )
        response = session.get( feed.url, timeout=5 )
        self._writeString( response.text )

    def getFeed(self, subPath) -> FeedEntry:
        feedList = self.getFeedList()
        if not feedList:
            return None
        
        for feed in feedList:
            if feed.feedId == subPath:
                return feed
        return None

    def getFeedList(self) -> List[ FeedEntry ]:
        data = self.server.dataObject
        if data is None:
            return []
        return data.feed.getList()
    
    def _respond404(self):
        self.send_response(404)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
        content = f"""<html>
    <body>
        404 resource not found
    </body>
</html>
"""
        self._writeString( content )
    
    def _writeString(self, content):
        encoded = content.encode("utf8")                                # NOTE: must return a bytes object!
        self.wfile.write( encoded )

    ## =====================================================================

    def log_message(self, format, *args):
        ## prevent logging
        return


## ======================================================


class RSSServer( socketserver.TCPServer ):

    def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True):
        super().__init__( server_address, RequestHandlerClass, bind_and_activate )
        self.dataObject = None


## ======================================================


class RSSServerManager():

    PORT = 8080
    Handler = RSSRequestHandler
#     Handler = http.server.SimpleHTTPRequestHandler
    
    def __init__(self):
        socketserver.TCPServer.allow_reuse_address = True
        self._service = None
        self._thread = None
        
        self.dataObject = None

    def attachData(self, dataObject: DataObject):
        self.dataObject = dataObject
        if self._service is not None:
            self._service.dataObject = dataObject

    @synchronized
    def start(self):
        if self._service is not None:
            ## already started
            return
        self._thread = threading.Thread(target=self._run, args=())
        self._thread.start()
    
    @synchronized
    def stop(self):
        if self._service is None:
            ## not started
            return
        _LOGGER.info( "stopping feed server" )
        serverThread = self._thread     ## self._thread will be null-ed soon
        self._shutdown_service()
        serverThread.join()

    def _run(self):
        with RSSServer(("", RSSServerManager.PORT), RSSServerManager.Handler) as httpd:
            self._service = httpd
            self._service.dataObject = self.dataObject
            try:
                _LOGGER.info("serving at port %s", RSSServerManager.PORT)
                httpd.allow_reuse_address = True
                httpd.serve_forever()
    #             httpd.handle_request()
            finally:
                self._service.server_close()
                self._service = None
                self._thread = None
        _LOGGER.info( "server thread ended" )
        
    @synchronized
    def _shutdown_service(self):
        if self._service is None:
            return
        self._service.shutdown()

## ============================================================


def start_server():
    PORT = 8080
    Handler = RSSRequestHandler
#     Handler = http.server.SimpleHTTPRequestHandler
    
#     logger.configure_console()
    
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            print("serving at port", PORT)
            httpd.allow_reuse_address = True
            httpd.serve_forever()
#             httpd.handle_request()
        finally:
            httpd.shutdown()
            httpd.server_close()
    

## podcast: https://feedgen.kiesow.be/
def generate_feed():
    fg = FeedGenerator()
    fg.id('http://lernfunk.de/media/654321')
    fg.title('Some Testfeed')
    fg.author( {'name':'John Doe','email':'john@example.de'} )
    fg.link( href='http://example.com', rel='alternate' )
    fg.logo('http://ex.com/logo.jpg')
    fg.subtitle('This is a cool feed!')
    fg.link( href='http://larskiesow.de/test.atom', rel='self' )
    fg.language('en')
    
    return fg.rss_str(pretty=True) # Get the RSS feed as string
    #print( "feed:\n", rssfeed )

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

try:
    ## following import success only when file is directly executed from command line
    ## otherwise will throw exception when executing as parameter for "python -m"
    # pylint: disable=W0611
    import __init__
except ImportError:
    ## when import fails then it means that the script was executed indirectly
    ## in this case __init__ is already loaded
    pass

import logging

# from PyQt5.QtWidgets import QApplication

from rsscast import logger
from rsscast.rss.rssgenerator import generate_channel_rss
from rsscast.rss.rsschannel import RSSChannel
from rsscast.source.youtube.ytfeedparser import parse_rss_content

from testrsscast.data import read_data


_LOGGER = logging.getLogger(__name__)


## ============================= main section ===================================


def main():
    logger.configure_console()

    feedContent = read_data( "yt_feed_latino_short.xml" )
    # feedContent = read_data( "yt_feed_konfederacja.xml" )

    rssChannel = RSSChannel()
    parse_rss_content(rssChannel, feedContent )
    generate_channel_rss( "test/abc", rssChannel )


if __name__ != '__main__':
    main()

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
except ImportError as error:
    ## when import fails then it means that the script was executed indirectly
    ## in this case __init__ is already loaded
    pass

import sys
import logging
import argparse

# from PyQt5.QtWidgets import QApplication

import rsscast.logger as logger
from rsscast.rss.rssconverter import convert_rss_content
from rsscast.rss.rssserver import RSSServerManager

from testrsscast.data import read_data


## ============================= main section ===================================


if __name__ != '__main__':
    sys.exit(0)


parser = argparse.ArgumentParser(description='RSS Cast Example')
# parser.add_argument('-lud', '--loadUserData', action='store_const', const=True, default=False, help='Load user data' )
# parser.add_argument('--minimized', action='store_const', const=True, default=False, help='Start minimized' )

args = parser.parse_args()


# logFile = logger.get_logging_output_file()
# logger.configure( logFile )

logger.configure_console()

_LOGGER = logging.getLogger(__name__)


hostAddress = RSSServerManager.getPrimaryIp()

fileContent = read_data( "yt_latino_short.rss" )
# fileContent = read_data( "yt_konfederacja.rss" )
convert_rss_content( hostAddress, "test/abc", fileContent )


#         read_rss( "https://www.youtube.com/feeds/videos.xml?channel_id=UCbbz3_jH582xS93hxszPvjQ" )

# read_rss( "http://www.youtube.com/feeds/videos.xml?user=TheNWOChannelTV" )

# read_rss( "http://rss.cnn.com/rss/edition.rss" )
#         read_rss( "https://blogs.nasa.gov/stationreport/feed/" )

# read_rss( "http://www.google.pl" )
# read_rss( "http://www.onet.pl" )
#         read_rss( 'https://www.nasa.gov/rss/dyn/lg_image_of_the_day.rss' )

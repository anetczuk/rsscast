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

import unittest
import logging
# import datetime
# import pandas

from rsscast.rss.rssclient import read_rss
from testrsscast.data import get_data_path


_LOGGER = logging.getLogger(__name__)


class RssClientTest(unittest.TestCase):

    def setUp(self):
        ## Called before testfunction is executed
        pass

    def tearDown(self):
        ## Called after testfunction was executed
        pass

#     def test_read_rss_localfile(self):
#         filePath = get_data_path( "station.xml" )
#         read_rss( filePath )

    def test_read_rss_url(self):
#         read_rss( "https://www.youtube.com/feeds/videos.xml?channel_id=UCbbz3_jH582xS93hxszPvjQ" )

        read_rss( "http://rss.cnn.com/rss/edition.rss" )
#         read_rss( "https://blogs.nasa.gov/stationreport/feed/" )

#         read_rss( "http://www.onet.pl" )
#         read_rss( 'https://www.nasa.gov/rss/dyn/lg_image_of_the_day.rss' )
#         read_rss( filePath )

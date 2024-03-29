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

from rsscast.source.youtube.ytfeedreader import read_yt_rss_from_source

from testrsscast.data import read_data


class YTFeedReaderTest(unittest.TestCase):
    def setUp(self):
        ## Called before testfunction is executed
        pass

    def tearDown(self):
        ## Called after testfunction was executed
        pass

    def test_read_yt_channel_rss_from_source(self):
        # get RSS address from channel webpage
        siteContent = read_data( "yt_html_wideoprezentacje.html" )

        rss_url_data = read_yt_rss_from_source( siteContent )
        self.assertTrue( rss_url_data is not None )
        self.assertEqual( rss_url_data[0], "wideoprezentacje" )
        self.assertEqual( rss_url_data[1],
                          "https://www.youtube.com/feeds/videos.xml?channel_id=UCViVL2aOkLWKcFVi0_p6u6g" )

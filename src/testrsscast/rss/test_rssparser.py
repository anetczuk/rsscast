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

from rsscast.rss.rssparser import RSSChannel, RSSItem

from testrsscast.data import read_data


class RSSChannelTest(unittest.TestCase):
    def setUp(self):
        ## Called before testfunction is executed
        pass

    def tearDown(self):
        ## Called after testfunction was executed
        pass

    def test_parse(self):
        feedContent = read_data( "yt_latino_short.rss" )
        channel = RSSChannel()
        channel.parse( feedContent )

        self.assertTrue( channel != None )
        self.assertEqual( channel.title, "YouTube Latinoamérica" )
        self.assertEqual( channel.link, "https://www.youtube.com/channel/UCBrGE6cmFbcwzlwAyIDMGpw" )
        self.assertEqual( channel.publishDate, "2013-10-07T19:27:52+00:00" )

        items = channel.items
        self.assertTrue( items != None )
        self.assertEqual( len(items), 3 )

        self.assertEqual( items[0].id, "yt:video:omY5FahfTrI" )
        self.assertEqual( items[0].link, "https://www.youtube.com/watch?v=omY5FahfTrI" )
        self.assertEqual( items[0].title, "#RegresoAClases con Julioprofe" )
        self.assertEqual( items[0].summary[0:26], "Ya estamos más que listos " )
        self.assertEqual( items[0].publishDate, "2020-08-24T20:58:16+00:00" )
        self.assertEqual( items[0].thumb_url, "https://i4.ytimg.com/vi/omY5FahfTrI/hqdefault.jpg" )
        self.assertEqual( items[0].thumb_width, "480" )
        self.assertEqual( items[0].thumb_height, "360" )

        self.assertEqual( items[1].id, "yt:video:kztwPl8QQTA" )
        self.assertEqual( items[2].id, "yt:video:DXU6PBpv-eI" )

    def test_update(self):
        channelFrom = RSSChannel()
        channelFrom.addItem( RSSItem( itemId="xxx1", link="aaa1" ) )
        channelFrom.addItem( RSSItem( itemId="xxx2" ) )
        self.assertEqual( len( channelFrom.items ), 2 )

        channelTo = RSSChannel()
        channelTo.addItem( RSSItem( itemId="xxx1", link="aaa1-b" ) )
        channelTo.update( channelFrom )
        self.assertEqual( len( channelTo.items ), 2 )
        self.assertEqual( channelTo.items[0].link, "aaa1-b" )

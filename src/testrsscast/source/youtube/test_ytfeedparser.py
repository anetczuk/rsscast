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
import datetime

from rsscast.source.youtube.ytfeedparser import parse_rss_content

from testrsscast.data import read_data


class YTFeedParserTest(unittest.TestCase):
    def setUp(self):
        ## Called before testfunction is executed
        pass

    def tearDown(self):
        ## Called after testfunction was executed
        pass

    def test_parse_latino(self):
        feedContent = read_data( "yt_feed_latino_short.xml" )
        channel = parse_rss_content(feedContent)

        self.assertTrue( channel is not None )
        self.assertEqual( channel.title, "YouTube Latinoamérica" )
        self.assertEqual( channel.link, "https://www.youtube.com/channel/UCBrGE6cmFbcwzlwAyIDMGpw" )
        self.assertEqual( channel.publishDate, datetime.datetime(2013, 10, 7, 19, 27, 52,
                                                                 tzinfo=datetime.timezone.utc) )
        self.assertEqual( channel.getPublishDateRFC(), "Mon, 07 Oct 2013 19:27:52 +0000" )

        items = channel.items
        self.assertTrue( items is not None )
        self.assertEqual( len(items), 3 )

        self.assertEqual( items[0].id, "yt:video:omY5FahfTrI" )
        self.assertEqual( items[0].link, "https://www.youtube.com/watch?v=omY5FahfTrI" )
        self.assertEqual( items[0].title, "#RegresoAClases con Julioprofe" )
        self.assertEqual( items[0].summary[0:26], "Ya estamos más que listos " )
        self.assertEqual( items[0].publishDate, datetime.datetime(2020, 8, 24, 20, 58, 16,
                                                                  tzinfo=datetime.timezone.utc) )
        self.assertEqual( items[0].getPublishDateRFC(), "Mon, 24 Aug 2020 20:58:16 +0000" )
        self.assertEqual( items[0].thumb_url, "https://i4.ytimg.com/vi/omY5FahfTrI/hqdefault.jpg" )
        self.assertEqual( items[0].thumb_width, "480" )
        self.assertEqual( items[0].thumb_height, "360" )

        self.assertEqual( items[1].id, "yt:video:kztwPl8QQTA" )
        self.assertEqual( items[2].id, "yt:video:DXU6PBpv-eI" )

    def test_parse_przygody(self):
        feedContent = read_data( "yt_feed_przygody.xml" )
        channel = parse_rss_content(feedContent)

        self.assertTrue( channel is not None )
        self.assertEqual( "Przygody Przedsiębiorców", channel.title )
        self.assertEqual( "https://www.youtube.com/channel/UCjHJwETvfm2y9vPIyJpVgZA", channel.link )
        self.assertEqual( channel.publishDate,
                          datetime.datetime(2017, 6, 20, 15, 32, 16, tzinfo=datetime.timezone.utc) )
        self.assertEqual( "Tue, 20 Jun 2017 15:32:16 +0000", channel.getPublishDateRFC() )

        items = channel.items
        self.assertTrue( items is not None )
        self.assertEqual( len(items), 15 )

        self.assertEqual( items[0].id, "yt:video:dsqoDfskU7k" )
        self.assertEqual( items[0].link, "https://www.youtube.com/watch?v=dsqoDfskU7k" )
        self.assertEqual( items[0].title, "WYJĄTKOWOŚĆ ZŁOTEJ 44 [SUBSKRYBUJ] RAFAŁ ZAORSKI" )
        self.assertEqual( items[0].summary[0:26], "" )
        self.assertEqual( items[0].publishDate,
                          datetime.datetime(2023, 12, 30, 23, 25, 5, tzinfo=datetime.timezone.utc) )
        self.assertEqual( items[0].getPublishDateRFC(), "Sat, 30 Dec 2023 23:25:05 +0000" )
        self.assertEqual( items[0].thumb_url, "https://i1.ytimg.com/vi/dsqoDfskU7k/hqdefault.jpg" )
        self.assertEqual( items[0].thumb_width, "480" )
        self.assertEqual( items[0].thumb_height, "360" )

        self.assertEqual( items[1].id, "yt:video:7wqXJ2njwLU" )
        self.assertEqual( items[2].id, "yt:video:E1xPm9olCuM" )

    def test_parse_404(self):
        feedContent = read_data( "yt_feed_404.xml" )
        channel = parse_rss_content(feedContent)
        self.assertTrue( channel is None )

    def test_parse_playlist(self):
        feedContent = read_data( "yt_feed_playlist_gwiazdowski.xml" )
        channel = parse_rss_content(feedContent)

        self.assertTrue( channel is not None )
        self.assertEqual( "Gwiazdowski mówi Interii", channel.title )
        self.assertEqual( "https://www.youtube.com/channel/UC0DpwRtGw4K9tNLnUJqx9qA", channel.link )
        self.assertEqual( channel.publishDate, datetime.datetime(2022, 9, 6, 5, 28, 43, tzinfo=datetime.timezone.utc) )
        self.assertEqual( channel.getPublishDateRFC(), "Tue, 06 Sep 2022 05:28:43 +0000" )

        items = channel.items
        self.assertTrue( items is not None )
        self.assertEqual( len(items), 15 )

        self.assertEqual( "yt:video:KQYfHfqjV1Q", items[0].id )
        self.assertEqual( "https://www.youtube.com/watch?v=KQYfHfqjV1Q", items[0].link )
        self.assertEqual( "Gwiazdowski mówi Interii. Odc. 1: Kłamstwo bardziej atrakcyjne od prawdy", items[0].title )
        self.assertEqual( "Felietonista Interii Bizne", items[0].summary[0:26] )
        self.assertEqual( items[0].publishDate, datetime.datetime(2022, 9, 6, 14, 30, 4, tzinfo=datetime.timezone.utc) )
        self.assertEqual( items[0].getPublishDateRFC(), "Tue, 06 Sep 2022 14:30:04 +0000" )
        self.assertEqual( "https://i4.ytimg.com/vi/KQYfHfqjV1Q/hqdefault.jpg", items[0].thumb_url )
        self.assertEqual( "480", items[0].thumb_width )
        self.assertEqual( "360", items[0].thumb_height )

        self.assertEqual( "yt:video:CortTsAlPD0", items[1].id )
        self.assertEqual( "yt:video:uQnqMPe4S08", items[2].id )

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
from testrsscast.data import read_data

from rsscast.datatypes import FeedEntry


class FeedEntryTest(unittest.TestCase):
    def setUp(self):
        ## Called before testfunction is executed
        self.entry = FeedEntry()

    def tearDown(self):
        ## Called after testfunction was executed
        self.entry = None

    def test_fixRepeatedTitles(self):
        feedContent = read_data( "yt_latino_title_repeat.rss" )
        self.entry.updateFromContent( feedContent )

        self.entry.fixRepeatedTitles()

        channel = self.entry.channel
        self.assertEqual( channel.size(), 3 )

        self.assertEqual( channel.get(0).title, "#RegresoAClases con Julioprofe" )
        self.assertEqual( channel.get(1).title, "Desde Casa #Conmigo" )
        self.assertEqual( channel.get(2).title, "Desde Casa #Conmigo [R2]" )

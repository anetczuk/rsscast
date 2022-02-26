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
import re

from rsscast.rss.rssconverter import fix_url, fix_url_text


class RSSConverterTest(unittest.TestCase):
    def setUp(self):
        ## Called before testfunction is executed
        pass

    def tearDown(self):
        ## Called after testfunction was executed
        pass

    def test_fix_url_valid(self):
        fixedURL = fix_url( "https://www.xyz.com/aaa" )
        self.assertIsNone( fixedURL )

    def test_fix_url_semicolon(self):
        fixedURL = fix_url( "https://www.xyz.com/aaa?bbb=ccc&sub;ddd=1" )
        self.assertEqual( fixedURL, "https://www.xyz.com/aaa?bbb=ccc&amp;subddd=1" )

    def test_fix_url_text_semicolon(self):
        text = "Word https://www.xyz.com/aaa?bbb=ccc&sub;ddd=1 other word http://example.com/blah"
        fixedText = fix_url_text( text )
        self.assertEqual( fixedText, "Word https://www.xyz.com/aaa?bbb=ccc&amp;subddd=1 other word http://example.com/blah" )
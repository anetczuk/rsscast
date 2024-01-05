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

import logging

from rsscast.rss.rsschannel import RSSChannel
from rsscast.source.youtube.ytfeedparser import parse_rss
from rsscast.source.youtube.ytdlpparser import parse_playlist_raw, parse_playlist_lazy


_LOGGER = logging.getLogger(__name__)


## ============================================================


def parse_url( feedId, feedUrl, write_content=True, known_items=None ) -> RSSChannel:
    # 'parse_rss' for backward compatibility
    channel = parse_rss(feedId, feedUrl, write_content)
    if channel:
        return channel
    if not known_items:
        # empty list
        channel = parse_playlist_raw(feedUrl, items_num=9999)
    else:
        channel = parse_playlist_lazy(feedUrl, known_items=known_items)
    if channel:
        return channel
    # no data found
    return RSSChannel()

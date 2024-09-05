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

import sys
import logging
import json

from rsscast import logger
from rsscast.rss.rsschannel import RSSChannel
from rsscast.source.parser import parse_url


_LOGGER = logging.getLogger(__name__)


def parse(url, max_fetch=10) -> RSSChannel:
    return parse_url("test-channel", url, write_content=False, max_fetch=max_fetch)


def get_json(obj):
    return json.loads(
        json.dumps(obj, default=lambda o: getattr(o, '__dict__', str(o)))
    )


def test01():
    channel_data: RSSChannel = parse("http://www.youtube.com/feeds/videos.xml?user=KNPvsUE", max_fetch=2)

    channel_data.sort()
    print("extracted rss channel data:")
    # ret_dict = get_json(channel_data)
    # pprint.pprint( ret_dict )
    print("playlist case found items:", channel_data.size())
    if channel_data.size() < 1:
        print("FAILED")
        sys.exit(1)


def test02():
    channel_data: RSSChannel = parse("https://www.youtube.com/playlist?list=PLvLrA9jH7wQixazuO4ZcAU9eyqVAnpMqi",
                                     max_fetch=2)

    channel_data.sort()
    print("extracted rss channel data:")
    # ret_dict = get_json(channel_data)
    # pprint.pprint( ret_dict )
    print("playlist case found items:", channel_data.size())
    if channel_data.size() < 1:
        print("FAILED")
        sys.exit(1)


def main():
    logger.configure()

    test01()
    test02()

    _LOGGER.info( "tests completed" )


# =============================================================


if __name__ == '__main__':
    main()
    sys.exit(0)

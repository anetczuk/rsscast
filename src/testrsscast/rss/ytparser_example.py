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
import json
import pprint

from rsscast import logger
from rsscast.rss.rssparser import RSSChannel
from rsscast.rss.ytparser import parse_url


## https://github.com/yt-dlp/yt-dlp


def parse(url) -> RSSChannel:
    return parse_url("xxx", url, write_content=False)


def get_json(obj):
    return json.loads(
        json.dumps(obj, default=lambda o: getattr(o, '__dict__', str(o)))
    )


def main():
    logger.configure()

    # check case - should return 15 items
    data: RSSChannel = parse("http://www.youtube.com/feeds/videos.xml?user=KNPvsUE")
    print("user case found items:", data.size())
    
    # check case - should return 15 items
    # Niebezpiecznik
    data: RSSChannel = parse("https://www.youtube.com/feeds/videos.xml?channel_id=UCe6nK69Yc1zna7QSJEfA9pw")
    print("channel case found items:", data.size())
    
    # check case - should return 15 items
    data: RSSChannel = parse("https://www.youtube.com/user/KNPvsUE")
    print("channel case found items:", data.size())
    
    # check case - should return 15 items
    data: RSSChannel = parse("https://www.youtube.com/@NiebezpiecznikTV/videos")
    print("playlist case found items:", data.size())

    # wideoprezentacje sublist
    data: RSSChannel = parse("https://www.youtube.com/playlist?list=PLE58asSGZSR3PC9dKk9taK9YDvlcUphzv")
    print("playlist case found items:", data.size())
    pprint.pprint( get_json(data) )


# =============================================================


if __name__ == '__main__':
    main()
    sys.exit(0)

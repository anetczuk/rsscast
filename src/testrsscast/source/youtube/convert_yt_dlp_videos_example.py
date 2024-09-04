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
from rsscast.rss.rsschannel import RSSChannel

from rsscast.source.youtube.convert_yt_dlp import parse_playlist


def get_json(obj):
    return json.loads(
        json.dumps(obj, default=lambda o: getattr(o, '__dict__', str(o)))
    )


def main():
    logger.configure()

    # przygody przedsiebiorcow
    url = "https://www.youtube.com/c/PrzygodyPrzedsi%C4%99biorc%C3%B3w/videos"

    # info_dict = fetch_info(url, items_num=999999)
    # info_dict["entries"] = "xxx"
    # pprint.pprint( info_dict )
    # return

    channel_data: RSSChannel = parse_playlist(url)
    channel_data.sort()
    print("extracted rss channel data:")
    ret_dict = get_json(channel_data)
    pprint.pprint( ret_dict )
    print("playlist case found items:", channel_data.size())


# =============================================================


if __name__ == '__main__':
    main()
    sys.exit(0)

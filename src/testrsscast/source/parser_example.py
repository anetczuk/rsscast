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

from rsscast.source.youtube.ytdlpparser import parse_playlist_raw
from rsscast.source.parser import parse_url


## https://github.com/yt-dlp/yt-dlp


def parse(url) -> RSSChannel:
    return parse_url("xxx", url, write_content=False)


def get_json(obj):
    return json.loads(
        json.dumps(obj, default=lambda o: getattr(o, '__dict__', str(o)))
    )


def main():
    logger.configure()

    # info_dict = fetch_info("https://www.youtube.com/watch?v=oONGCDBU32I")
    # pprint.pprint(info_dict)
    # return

    # # check case - should return 15 items
    # data: RSSChannel = parse("http://www.youtube.com/feeds/videos.xml?user=KNPvsUE")
    # print("user case found items:", data.size())
    #
    # # check case - should return 15 items
    # # Niebezpiecznik
    # data: RSSChannel = parse("https://www.youtube.com/feeds/videos.xml?channel_id=UCe6nK69Yc1zna7QSJEfA9pw")
    # print("channel case found items:", data.size())

    # # przygody przedsiebiorcow
    # # check case - should return 15 items
    # channel_data: RSSChannel = parse("https://www.youtube.com/feeds/videos.xml?channel_id=UCjHJwETvfm2y9vPIyJpVgZA")
    # channel_data.sort()
    # print("channel case found items:", channel_data.size())
    # print("extracted rss channel data:")
    # ret_dict = get_json(channel_data)
    # pprint.pprint( ret_dict )

    url = "https://www.youtube.com/@PrzygodyPrzedsiebiorcow/videos"
    channel_data: RSSChannel = parse_playlist_raw(url, items_num=10)
    channel_data.sort()
    print("playlist case found items:", channel_data.size())
    print("extracted rss channel data:")
    ret_dict = get_json(channel_data)
    pprint.pprint( ret_dict )

    # # check case - should return 15 items
    # data: RSSChannel = parse("https://www.youtube.com/user/KNPvsUE")
    # print("channel case found items:", data.size())
    #
    # # check case - should return 15 items
    # data: RSSChannel = parse("https://www.youtube.com/@NiebezpiecznikTV/videos")
    # print("playlist case found items:", data.size())

    # ## gwaizdowski
    # url = "https://www.youtube.com/playlist?list=PLC9xjKm8G0LpgFgi-eF4YgvtMuogd1dHw"
    # channel_data: RSSChannel = parse_playlist_raw(url, items_num=10)     # gwiazdowski
    # channel_data.sort()
    # print("playlist case found items:", channel_data.size())
    # print("extracted rss channel data:")
    # ret_dict = get_json(channel_data)
    # pprint.pprint( ret_dict )

    # content = generate_items_rss( channel_data, channel_data.items, "host.xxx", "feedxxx", "/tmp/xxx",
    #                               store=False, check_local=False )
    # print(content)


# =============================================================


if __name__ == '__main__':
    main()
    sys.exit(0)

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
from rsscast.source.youtube.ytconverter import convert_to_audio, parse_playlist, get_yt_duration
from rsscast.rss.rsschannel import RSSChannel


_LOGGER = logging.getLogger(__name__)


def get_json(obj):
    return json.loads(
        json.dumps(obj, default=lambda o: getattr(o, '__dict__', str(o)))
    )


def test_01():
    url = 'https://www.youtube.com/watch?v=gNs_9xFisdE'
    duration = get_yt_duration( url )
    if duration != 1152:
        _LOGGER.error( "===== test failed: unable to read video proper length" )
    else:
        length_m = int(duration / 60)
        length_s = int(duration % 60)
        _LOGGER.info( f'length: {duration} = {length_m}m {length_s}s' )

    output_path = "/tmp/test_convert_00.data"
    _LOGGER.info( "converting video: %s into %s", url, output_path )

    status = convert_to_audio( url, output_path )
    _LOGGER.info( "conversion status: %s", status )
    if not status:
        _LOGGER.error( "===== test failed: unable to convert video" )
        sys.exit(1)


def test_02():
    url = "https://www.youtube.com/watch?v=1cpyexbmMyU"
    output_path = "/tmp/test_convert_01.data"
    _LOGGER.info( f"downloading {url}" )
    status = convert_to_audio( url, output_path )
    _LOGGER.info( "conversion status: %s", status )
    if not status:
        _LOGGER.error( "===== test failed: unable to convert video" )
        sys.exit(1)


def test_03():
    url = "https://www.youtube.com/watch?v=ZGMNaHINvuI"
    #url = "https://www.youtube.com/watch?v=2p8OTosmFHU"
    output_path = "/tmp/test_convert_02.data"
    _LOGGER.info( f"downloading {url}" )
    status = convert_to_audio( url, output_path )
    _LOGGER.info( "conversion status: %s", status )
    if not status:
        _LOGGER.error( "===== test failed: unable to convert video" )
        sys.exit(1)


def test_convert_to_audio():
    converted = convert_to_audio( "https://www.youtube.com/watch?v=BLRUiVXeZKU", "/tmp/yt_example.mp3" )

    ## long file: 3h 58m
    # converted = convert_to_audio( "https://www.youtube.com/watch?v=C9HrMN9BjfY", "/tmp/yt_example.mp3" )

    # converted = convert_to_audio( "https://www.youtube.com/watch?v=cJuO985zF8E", "/tmp/yt_example.mp3" )

    print("converted:", converted)
    if not converted:
        print("FAILED")
        sys.exit(1)


def test_parse_playlist():
    # ## playlist - gwiazdowski
    # url = "https://www.youtube.com/playlist?list=PLC9xjKm8G0LpgFgi-eF4YgvtMuogd1dHw"
    # info_dict = fetch_info(url, items_num=999999)
    # info_dict["entries"] = "xxx"
    # pprint.pprint( info_dict )
    # return

    ## playlist - youtube latino
    url = "https://www.youtube.com/playlist?list=PL1ebpFrA3ctH0QN6bribofTNpG4z2loWy"
    known = ["https://www.youtube.com/watch?v=aAbfzUJLJJE", "https://www.youtube.com/watch?v=3Q1DIHK2AIw"]

    channel_data: RSSChannel = parse_playlist(url, known)
    channel_data.sort()
    print("playlist case found items:", channel_data.size())

    if channel_data.size() != 2:
        print("FAILED")
        sys.exit(1)


def main():
    logger.configure_console()

    test_convert_to_audio()

    test_parse_playlist()

    # test_01()

    # test_02()

    test_03()

    _LOGGER.info( "tests completed" )


if __name__ == '__main__':
    main()

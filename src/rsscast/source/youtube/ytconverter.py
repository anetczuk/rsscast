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
import random

from rsscast.rss.rsschannel import RSSChannel

from rsscast.source.youtube.convert_pytube import get_yt_duration as get_yt_duration_pytube

from rsscast.source.youtube.convert_yt_dlp import is_video_available as is_video_available_yt_dlp
from rsscast.source.youtube.convert_yt_dlp import parse_playlist as parse_playlist_yt_dlp
from rsscast.source.youtube.convert_yt_dlp import reduce_info as reduce_info_yt_dlp
from rsscast.source.youtube.convert_yt_dlp import convert_info_to_channel as convert_info_to_channel_yt_dlp

from rsscast.source.youtube.convert_ddownr_com import convert_yt as convert_yt_ddownr
# from rsscast.source.youtube.convert_pytube import convert_yt as convert_yt_pytube
from rsscast.source.youtube.convert_y2down_cc import convert_yt as convert_yt_y2down
# from rsscast.source.youtube.convert_youtube_dl import convert_yt as convert_yt_youtube_dl
from rsscast.source.youtube.convert_yt_dlp import convert_yt as convert_yt_yt_dlp
from rsscast.source.youtube.convert_yt1s_com import convert_yt as convert_yt_yt1s
from rsscast.source.youtube.ytwebconvert import check_is_mp3


_LOGGER = logging.getLogger(__name__)


WEB_CONVERTERS = [  # convert_yt_pytube,        # conversion from mp4 to mp3 needed
                  # convert_yt_youtube_dl,    # too old on RPi
                  convert_yt_ddownr, convert_yt_yt1s, convert_yt_y2down]


## ===================================================================


def is_video_available(video_url) -> bool:
    return is_video_available_yt_dlp(video_url)


## requires "youtube_dl"
def get_yt_duration( link ):
    return get_yt_duration_pytube( link )
    # return get_yt_duration_pafy( link )


# def get_yt_duration_pafy( link ):
#     video = pafy.new( link )
#     return video.length


def parse_playlist(page_url, known_items=None, max_fetch=10) -> RSSChannel:
    return parse_playlist_yt_dlp(page_url, known_items, max_fetch)


def convert_info_to_channel(info_dict) -> RSSChannel:
    return convert_info_to_channel_yt_dlp(info_dict)


def reduce_info(info_dict):
    reduce_info_yt_dlp(info_dict)


## ===================================================================


def convert_to_audio( link, output, mimicHuman=True ) -> bool:
    converters_list = list(WEB_CONVERTERS)
    random.shuffle(converters_list)

    for converter in converters_list:
        try:
            succeed = converter( link, output, mimicHuman )
            if not succeed:
                _LOGGER.error( f"failed to convert '{link}' - process failed" )
                continue
        except Exception:           # pylint: disable=broad-except
            _LOGGER.exception("unable to get audio from %s", link)
            continue

        if not check_is_mp3(output):
            _LOGGER.error( f"failed to convert '{link}' - invalid file" )
            continue

        # succeed
        return True

    ## yt_dlp natively stores audio in MP4 format with causes problems
    ## additional conversion step takes very long, so use the module
    ## as last possibility
    try:
        succeed = convert_yt_yt_dlp( link, output, mimicHuman )
        if not succeed:
            _LOGGER.error( f"failed to convert '{link}' - process failed" )
            return False
    except Exception:           # pylint: disable=broad-except
        _LOGGER.exception("unable to get audio from %s", link)
        return False

    if not check_is_mp3(output):
        _LOGGER.error( f"failed to convert '{link}' - invalid file" )
        return False

    # succeed
    return True

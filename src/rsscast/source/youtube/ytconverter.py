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

import os
import logging

from pytube import YouTube

import filetype

from rsscast.source.youtube.ytwebconvert import convert_yt_yt1s, convert_yt_y2down
from rsscast.source.youtube.ytdlpparser import download_audio


_LOGGER = logging.getLogger(__name__)


## ===================================================================


## requires "youtube_dl"
def get_yt_duration( link ):
    return get_yt_duration_pytube( link )
    # return get_yt_duration_pafy( link )


## returns value in seconds
def get_yt_duration_pytube( link ):
    try:
        yt = YouTube( link )
        # pprint.pprint( yt.vid_info )
        video_info  = yt.vid_info
        status_info = video_info.get( "playabilityStatus", {} )
        status      = status_info.get( "status", "Ok" )
        if status == "ERROR":
            reason = status_info.get( "reason", "" )
            _LOGGER.error( "unable to get length of video, reason: %s", reason )
            return -1

        return yt.length
    except TypeError as e:
        _LOGGER.exception( "unable to get video duration: %s", e )
    return -1


# def get_yt_duration_pafy( link ):
#     video = pafy.new( link )
#     return video.length


## ===================================================================


def convert_yt( link, output, mimicHuman=True ):
    if download_audio(link, output, format_id="233"):
        return True
    if download_audio(link, output, format_id="140"):
        return True

    _LOGGER.warning( "unable to download data using 'yt_dlp' - using web converter" )

    succeed = convert_yt_yt1s( link, output, mimicHuman )
    if not succeed:
        _LOGGER.error( f"failed to convert '{link}' - process failed" )
        return False
    if os.path.isfile( output ) is False:
        _LOGGER.error( f"failed to convert '{link}' - missing file" )
        return False
    kind = filetype.guess( output )
    if kind is None:
        ## server respond with HTML page instead of audio file
        _LOGGER.warning( f"failed to convert '{link}' - trying other method" )
        os.remove( output )

        succeed = convert_yt_y2down( link, output )
        if not succeed:
            _LOGGER.error( f"failed to convert '{link}' - unable to find type #1" )
            os.remove( output )
            return False
        if os.path.isfile( output ) is False:
            _LOGGER.error( f"failed to convert '{link}' - unable to find type #2" )
            return False
        kind = filetype.guess( output )
        if kind is None:
            _LOGGER.error( f"failed to convert '{link}' - unable to find type #3" )
            os.remove( output )
            return False

    if kind.extension != "mp3":
        _LOGGER.error( f"failed to convert '{link}' - bad type ({kind.extension})" )
        os.remove( output )
        return False

    return True

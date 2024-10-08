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
from pytubefix import YouTube as YouTubeFix


_LOGGER = logging.getLogger(__name__)


## ===================================================================


## returns value in seconds
def get_yt_duration( link ):
    _LOGGER.debug( "getting video duration by pytube: %s", link )
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


## ===================================================================


def convert_yt( link, output, _mimicHuman=True ) -> bool:
    _LOGGER.info("pytube: converting youtube video %s", link)

    yt = YouTubeFix(link)
    # yt.streams.first().download(output_path=output)
    audio_download = yt.streams.filter(file_extension="mp3").first()
    if audio_download is not None:
        # mp3 stream found
        out_file = audio_download.download(output_path="/tmp")
        os.rename( out_file, output )

        _LOGGER.info("downloading completed")
        return True

    # audio_download = yt.streams.get_audio_only()
    # out_file = audio_download.download(output_path="/tmp")
    # os.rename( out_file, output )
    #
    # _LOGGER.info("downloading completed")
    # return True

    return False


# ## crashes with error:
# ##    pytube.exceptions.RegexMatchError: get_throttling_function_name: could not find match for multiple
# def convert_pytube( link, output, mimicHuman=True ):
#     yt = YouTube( link )
#     video = yt.streams.filter(only_audio=True).first()
#     out_file = video.download( output_path="/tmp" )
#     os.rename( out_file, output )
#     return True

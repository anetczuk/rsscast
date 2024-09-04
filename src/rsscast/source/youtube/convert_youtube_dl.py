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
from typing import Dict, Any

import youtube_dl


_LOGGER = logging.getLogger(__name__)


def convert_yt( link, _output, _mimicHuman=True ) -> bool:
    _LOGGER.info("youtube_dl: converting youtube video %s", link)

    ydl_opts: Dict[Any, Any] = {}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])

    _LOGGER.info("downloading completed")
    return True


# ### errors with 'uploader id'
# def convert_youtube_dl( video_url, output ):
#     video_info = youtube_dl.YoutubeDL().extract_info( url = video_url, download=False )
#     filename = f"{video_info['title']}.mp3"
#     options = { 'format': 'bestaudio/best',
#                 'keepvideo': False,
#                 'outtmpl': filename,
#                 }
#
#     with youtube_dl.YoutubeDL(options) as ydl:
#         ydl.download( [video_info['webpage_url']] )
#
#     print("Download complete... {}".format(filename))


# def convert_yt_dwnldr( link, output, mimicHuman=True ):
# #     ydl_opts = {
# #         'format': 'bestaudio/best',
# #         'postprocessors': [{
# #             'key': 'FFmpegExtractAudio',
# #             'preferredcodec': 'mp3',
# #             'preferredquality': '192',
# #         }],
# #     }
# #     with youtube_dl.YoutubeDL(ydl_opts) as ydl:
# #         ydl.download( ['https://www.youtube.com/watch?v=BaW_jenozKc'] )
#
#
#     ydl_opts = {}
#     with youtube_dl.YoutubeDL(ydl_opts) as ydl:
#         ydl.download( [link] )
#
#
# #     ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s.%(ext)s'})
# #
# #     with ydl:
# #         result = ydl.extract_info( link )
# #
# #     if 'entries' in result:
# #         # Can be a playlist or a list of videos
# #         video = result['entries'][0]
# #     else:
# #         # Just a video
# #         video = result
# #
# #     print(video)
# #     video_url = video['url']
# #     print(video_url)

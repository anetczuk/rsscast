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

import time
import logging
import json

import urllib

from rsscast.source.youtube.ytwebconvert import urlretrieve


_LOGGER = logging.getLogger(__name__)


## use https://y2down.cc/
def convert_yt( link, output, _mimicHuman=True ) -> bool:
    _LOGGER.info("y2down.cc: converting youtube video %s", link)

    ## https://loader.to/ajax/download.php?format=mp3&url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D1cpyexbmMyU
    escaped_link = urllib.parse.quote( link )
    convert_url = f"https://loader.to/ajax/download.php?format=mp3&url={escaped_link}"
    convert_response = urlretrieve( convert_url )
    convert_data = json.loads( convert_response )
    # _LOGGER.info( f"convert data {convert_data}" )
    if convert_data.get( "success", False ) is False:
        _LOGGER.error( f"failed to convert '{link}' - server response" )
        return False
    convert_id = convert_data.get( "id", None )
    if not convert_id:
        _LOGGER.error( f"failed to convert '{link}' - missing ID" )
        return False

    # content = convert_data.get( "content", "" )
    # content = base64.b64decode( content )
    # content = content.decode("utf-8")
    # print( f"content:\n{content}")

    _LOGGER.info( f"waiting for finish of conversion of {link}" )

    recent_progress_value    = 0
    stalled_progress_counter = 0
    while True:
        progress_link = f"https://loader.to/ajax/progress.php?id={convert_id}"
        progress_resp = urlretrieve( progress_link )
        progress_data = json.loads( progress_resp )
        _LOGGER.info( "received progress: %s %s", stalled_progress_counter, progress_data )
        if progress_data.get("success", 0) != 0:
            break
        progress_value = progress_data.get("progress", 0)
        if recent_progress_value == progress_value:
            stalled_progress_counter += 1
            if stalled_progress_counter >= 20:
                _LOGGER.info( "downloading stalled - breaking" )
                return False
        else:
            recent_progress_value = progress_value
            stalled_progress_counter = 0
        time.sleep( 3.0 )

    download_link = progress_data.get( "download_url" )
    if not download_link:
        return False

    _LOGGER.info( f"downloading content from {download_link}" )
    urlretrieve( download_link, output, write_empty=False )

    _LOGGER.info("downloading completed")
    return True

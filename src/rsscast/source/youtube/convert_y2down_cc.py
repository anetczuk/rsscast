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

    progress_link = f"https://loader.to/ajax/progress.php?id={convert_id}"
    download_url = None
    recent_response_data = None
    while True:

        status_timeout = True
        for _ in range(0, 20):
            time.sleep( 3.0 )

            progress_resp = urlretrieve( progress_link )
            response_data = json.loads( progress_resp )

            if recent_response_data == response_data:
                # no change
                continue
            status_timeout = False
            recent_response_data = response_data
            break

        if status_timeout:
            break

        status = response_data.get("success")
        if status == 0:
            # in progress
            _LOGGER.debug( f"received progress: {response_data}" )
            continue

        if status != 1:
            _LOGGER.error(f"unhandled response: {response_data}")
            return False

        # found url
        download_url = response_data.get("download_url")
        break

    if download_url is None:
        _LOGGER.error( "timeout reached during waiting for conversion of link %s", link )
        return False

    _LOGGER.info( f"downloading content from {download_url} to {output}" )
    urlretrieve( download_url, output, timeout=90, write_empty=False )

    _LOGGER.info("downloading completed")
    return True

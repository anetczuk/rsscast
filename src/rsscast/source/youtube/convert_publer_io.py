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
import time
import json

from rsscast.source.youtube.ytwebconvert import urlretrieve, get_curl_session, curl_get


_LOGGER = logging.getLogger(__name__)


def convert_yt( link, output, _mimicHuman=True ) -> bool:
    _LOGGER.info("publer.io: converting youtube video %s", link)

    session = get_curl_session( "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/116.0" )

    service_link = "https://ab.cococococ.com/ajax/download.php"
    params = {"url": link, "iphone": False}

    post_header = ['Referer: https://publer.io/']

    dataBuffer = curl_get( session, service_link, params, header_list=post_header )
    bodyOutput = dataBuffer.getvalue().decode('utf-8')

    response_data = json.loads( bodyOutput )
    job_id = response_data.get("job_id")
    if job_id is None:
        _LOGGER.error(f"unhandled response: {response_data}")
        return False

    _LOGGER.info( f"waiting for finish of conversion of {link}" )

    status_url = f"https://app.publer.io/api/v1/job_status/{job_id}"
    download_url = None
    for _ in range(0, 120):
        status_response = curl_get(session, status_url)
        response = status_response.getvalue()
        response_data = json.loads( response )
        status = response_data.get("status")
        if status == "complete":
            payload = response_data["payload"]
            item = payload[0]
            download_url = item["path"]
            break
        if status != "working":
            _LOGGER.error(f"unhandled response: {response_data}")
            return False

        time.sleep(1.0)

    if download_url is None:
        _LOGGER.error( "timeout reached during waiting for conversion" )
        return False

    output_video = f"{output}.vid"
    _LOGGER.info( f"downloading content from {download_url} to {output_video}" )
    urlretrieve( download_url, output_video, timeout=60, write_empty=False )

    _LOGGER.info("downloading completed")
    return True

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
import urllib


_LOGGER = logging.getLogger(__name__)


def convert_yt( link, output, _mimicHuman=True ) -> bool:
    _LOGGER.info("ddownr.com: converting youtube video %s", link)

    session = get_curl_session( "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/116.0" )

    service_link = "https://p.oceansaver.in/ajax/download.php"
    params = {"copyright": 0, "format": "mp3",
              "url": link, "api": "dfcb6d76f2f6a9894gjkege8a4ab232222"}
    dataBuffer = curl_get( session, service_link, params, header_list=[] )
    bodyOutput = dataBuffer.getvalue().decode('utf-8')

    response_data = None
    try:
        response_data = json.loads( bodyOutput )
    except json.decoder.JSONDecodeError:
        _LOGGER.error( "invalid response (expected JSON) from link %s - response: %s", link, bodyOutput )
        return False

    job_id = response_data.get("id")
    if job_id is None:
        _LOGGER.error( "invalid JSON from link %s - json: %s", link, response_data )
        return False

    _LOGGER.info( f"waiting for finish of conversion of {link}" )

    status_url = "https://p.oceansaver.in/ajax/progress.php"
    params = {"id": job_id}
    download_url = None
    recent_response_data = None
    while True:

        status_timeout = True
        for _i in range(0, 20):
            time.sleep(6.0)

            status_response = curl_get(session, status_url, params)
            response = status_response.getvalue()
            response_data = json.loads( response )

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
    try:
        urlretrieve( download_url, output, timeout=90, write_empty=False )
    except urllib.error.HTTPError:
        _LOGGER.exception("unable to download content from %s", download_url)
        return False

    _LOGGER.info("downloading completed")
    return True

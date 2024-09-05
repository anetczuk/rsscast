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
import random
import logging
import json

from rsscast.source.youtube.ytwebconvert import get_curl_session, curl_post, urldownload


_LOGGER = logging.getLogger(__name__)


## converting YT videos using webpage https://yt1s.com
def convert_yt( link, output, mimicHuman=True ) -> bool:
    _LOGGER.info("yt1s.com: converting youtube video %s", link)

    try:
        session = get_curl_session()

        mp3Data = get_mp3_data( session, link, mimicHuman )
        if mp3Data is None:
            return False

        vidId     = mp3Data[0]
        mp3Format = mp3Data[1]

        convertId = mp3Format['k']
#         dataSize  = mp3Format['size']

#         pprint( mp3Format )

        convert_url = "https://www.yt1s.com/api/ajaxConvert/convert"
        params = { 'vid': vidId,
                   'k': convertId }
        _LOGGER.debug( "sending convert request to %s\nparams: %s", convert_url, params )

        download_url = None
        recent_response_data = None
        for _ in range(0, 120):
            if mimicHuman:
                randTime = random.uniform( 1.0, 3.0 )
                time.sleep( randTime )
            else:
                time.sleep(1.0)

            status_response = curl_post( session, convert_url, params )
            response = status_response.getvalue()
            response_data = json.loads( response )

    #         print( "convert response:", data )
    #         pprint( data )

            if recent_response_data == response_data:
                # no change
                continue
            recent_response_data = response_data

            jsonStatus = response_data['status']
            if jsonStatus != "ok":
                _LOGGER.error( "invalid status:\n%s", jsonStatus )
                return False

            c_status = response_data['c_status']
            if c_status == "CONVERTING":
                # in progress
                continue

            if c_status == "CONVERTED":
                # completed
                download_url = response_data["dlink"]
                break

            ## {"status":"ok","mess":"","c_status":"CONVERTING","b_id":"6004d4c0d684ebb22f8b45ab","e_time":39}
            _LOGGER.error( "invalid status:\n%s", response_data )
            return False

        if download_url is None:
            _LOGGER.error( "timeout reached during waiting for conversion" )
            return False

        _LOGGER.info( "grabbing file: %s to %s", download_url, output )
        urldownload( download_url, output )

#         simple_download( download_url, output )
#         curl_download( session, download_url, output )

#         if mimicHuman:
#             randTime = random.uniform( 1.0, 3.0 )
#             time.sleep( randTime )

        ## done -- returning
        _LOGGER.info("downloading completed")
        return True

    except Exception as exc:                                               # pylint: disable=W0703
        _LOGGER.exception("Unexpected exception: %s", exc, exc_info=False)
        return False

    finally:
        session.close()

    return False


def get_media_size( link, mimicHuman=True ):
    try:
        session = get_curl_session()

        mp3Data = get_mp3_data( session, link, mimicHuman )
        if mp3Data is None:
            return None

        mp3Format = mp3Data[1]
        dataSize  = mp3Format['size']
        if dataSize is None:
            return None

        return dataSize

    finally:
        session.close()

    return None


def get_mp3_data( session, link, mimicHuman=True ):
    # # Read cookies
    # cookies = session.getinfo(pycurl.INFO_COOKIELIST)
    # # Print the cookies
    # print("Cookies are:")
    # for cookie in cookies:
    #     print(cookie)

#    _LOGGER.debug( "curl_post: accessing %s", link )
    # web_url = "https://yt1s.com/api/ajaxSearch/index"
    header_list = ['Referer: https://www.yt1s.com/en0ipr/youtube-to-mp3']
    web_url = "https://www.yt1s.com/api/ajaxSearch/index"
    params = {'q': link,
              'vt': 'mp3'}
    _LOGGER.debug( "sending request to %s\nparams: %s", web_url, params )
    dataBuffer = curl_post( session, web_url, params, header_list=header_list )
    bodyOutput = dataBuffer.getvalue().decode('utf-8')

    # _LOGGER.debug( "response:\n%s", bodyOutput )
    # _LOGGER.debug( "response:\n%s", bodyOutput[0:255] )

    data = json.loads( bodyOutput )

#         print( "request response:" )
#         pprint( data )

    jsonStatus = data['status']
    if jsonStatus != "ok":
        _LOGGER.warning( "invalid status:\n%s", bodyOutput )
        return None
    jsonMess = data['mess']
    if jsonMess != "":
        ## happens always for delayed premieres
        _LOGGER.warning( "invalid status while converting %s:\n%s\npremiere?", link, bodyOutput )
        return None

    if mimicHuman:
        randTime = random.uniform( 1.0, 3.0 )
        time.sleep( randTime )

    ## video ID, eg: "EE4U9qpErW8"
    vidId     = data["vid"]

    # pylint: disable=C0301
    ## convert key, like: "0+azXhfVIrnzRYKBCptsmBJiPRF1HVqa5l7v3sVU68OOkmCBRvmw/2jfMz2F1b42/wu2h1L4EoRSl7BxuLz3jxPrCyVYC2cF9udBFCDoF7T5kZpCBy5X"
    mp3Data   = data['links']['mp3']
    mp3Format = get_mp3_format_data( mp3Data )
    return ( vidId, mp3Format )


## get mp3 format from response dict
def get_mp3_format_data( mp3FormatDict ):
    if '256' in mp3FormatDict:
        return mp3FormatDict['256']
    keys = mp3FormatDict.keys()
    if len( keys ) < 1:
        raise Exception("There is no data in dictionary")
    ## get first key
    formatKey = next(iter( keys ))
    return mp3FormatDict[ formatKey ]

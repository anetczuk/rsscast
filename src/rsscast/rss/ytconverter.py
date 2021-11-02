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
import tempfile
from shutil import copyfile
import time
import random
import logging
from io import BytesIO
from urllib.parse import urlencode
import json

import pycurl
# import urllib.request
import requests

# from rsscast.pprint import pprint
# import youtube_dl


_LOGGER = logging.getLogger(__name__)


def convert_yt( link, output, mimicHuman=True ):
#     return convert_yt_dwnldr( link, output )
    return convert_yt_yt1s( link, output, mimicHuman )


## ===================================================================


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


## ===================================================================


def get_mp3_format_data( mp3FormatDict ):
    if '256' in mp3FormatDict:
        return mp3FormatDict['256']
    keys = mp3FormatDict.keys()
    if len( keys ) < 1:
        raise Exception("There is no data in dictionary")
    ## get first key
    formatKey = next(iter( keys ))
    return mp3FormatDict[ formatKey ]


## converting YT videos using webpage https://yt1s.com
def convert_yt_yt1s( link, output, mimicHuman=True ):
    dataBuffer = BytesIO()
    try:
        session = pycurl.Curl()
        session.setopt( pycurl.USERAGENT, "curl/7.58.0" )
        session.setopt( pycurl.FOLLOWLOCATION, True )        ## follow redirects
        session.setopt( pycurl.CONNECTTIMEOUT, 60 )          ## connection phase timeout
#         session.setopt( pycurl.TIMEOUT, 60 )                 ## whole request timeout (transfer?)
#         c.setopt( c.VERBOSE, 1 )

        params = {'q': link,
                  'vt': 'mp3'}

        dataBuffer = curl_post( session, "https://yt1s.com/api/ajaxSearch/index", params )
        bodyOutput = dataBuffer.getvalue().decode('utf-8')
#         _LOGGER.info( "response:\n%s", bodyOutput )

        data = json.loads( bodyOutput )

#         print( "request response:" )
#         pprint( data )
        
        jsonStatus = data['status']
        if jsonStatus != "ok":
            _LOGGER.warning( "invalid status:\n%s", bodyOutput )
            return False
        jsonMess = data['mess']
        if jsonMess != "":
            ## happens always for delayed premieres
            _LOGGER.warning( "invalid status while converting %s:\n%s\npremiere?", link, bodyOutput )
            return False

        if mimicHuman:
            randTime = random.uniform( 1.0, 3.0 )
            time.sleep( randTime )

        ## video ID, eg: "EE4U9qpErW8"
        vidId     = data["vid"]
        
        ## convert key, like: "0+azXhfVIrnzRYKBCptsmBJiPRF1HVqa5l7v3sVU68OOkmCBRvmw/2jfMz2F1b42/wu2h1L4EoRSl7BxuLz3jxPrCyVYC2cF9udBFCDoF7T5kZpCBy5X"
        mp3Data   = data['links']['mp3']
        mp3Format = get_mp3_format_data( mp3Data )
        convertId = mp3Format['k']
#         dataSize  = mp3Format['size']

#         pprint( mp3Format )

        params = { 'vid': vidId,
                   'k': convertId }
        dataBuffer = curl_post( session, "https://yt1s.com/api/ajaxConvert/convert", params )
        bodyOutput = dataBuffer.getvalue().decode('utf-8')
#         _LOGGER.info( "response:\n%s", bodyOutput )

        if mimicHuman:
            randTime = random.uniform( 1.0, 3.0 )
            time.sleep( randTime )

        data = json.loads( bodyOutput )
        
#         print( "convert response:" )
#         pprint( data )
        
        jsonStatus = data['status']
        if jsonStatus != "ok":
            _LOGGER.warning( "invalid status:\n%s", bodyOutput )
            return False
        jsonCStatus = data['c_status']
        if jsonCStatus != "CONVERTED":
            #TODO: handle case
            ## {"status":"ok","mess":"","c_status":"CONVERTING","b_id":"6004d4c0d684ebb22f8b45ab","e_time":39}
            _LOGGER.warning( "invalid status:\n%s", bodyOutput )
            return False

        dlink = data["dlink"]

        _LOGGER.info( "grabbing file: %s to %s", dlink, output )
        simple_download( dlink, output )
#         curl_download( session, dlink, output )

#         if mimicHuman:
#             randTime = random.uniform( 1.0, 3.0 )
#             time.sleep( randTime )

        ## done -- returning
        return True

#    except Exception as err:
#        logging.exception("Unexpected exception")
#        return False

    finally:
        session.close()

    return False


def curl_post( session, targetUrl, dataDict ):
#     _LOGGER.info( "accessing url: %s params: %s", targetUrl, dataDict )

    dataBuffer = BytesIO()
#     try:
    session.setopt( pycurl.URL, targetUrl )
    session.setopt( pycurl.POST, 1)
    session.setopt( pycurl.POSTFIELDS, urlencode( dataDict ))
    session.setopt( pycurl.WRITEDATA, dataBuffer )
    session.perform()
#         except Exception as err:
#             logging.exception("Unexpected exception")
#             return ""
#     finally:
#         session.close()
    return dataBuffer


def curl_download( session, sourceUrl, outputFile, repeatsOnFail=0 ):
    if repeatsOnFail < 0:
        repeatsOnFail = 0
    for _ in range(0, repeatsOnFail):
        try:
            curl_download_raw( session, sourceUrl, outputFile )
            ## done -- returning
            return
        except pycurl.error:
            _LOGGER.exception( "could not download file" )

    curl_download_raw( session, sourceUrl, outputFile )


def curl_download_raw( session, sourceUrl, outputFile ):
    fd, path = tempfile.mkstemp()
    try:
        session.setopt( pycurl.URL, sourceUrl )
        session.setopt( pycurl.POST, 0)
        with os.fdopen(fd, 'wb') as tmp:
            session.setopt( session.WRITEFUNCTION, tmp.write )
            session.perform()
        copyfile( path, outputFile )
    finally:
        _LOGGER.info( "removing temporary file: %s", path )
        os.remove( path )


def simple_download( sourceUrl, outputFile ):
#     urllib.request.urlretrieve( sourceUrl, outputFile )

    r = requests.get( sourceUrl )
    with open( outputFile, 'wb' ) as output:
        output.write( r.content )

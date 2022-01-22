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
import json
import re

import urllib.request as request
from urllib.parse import urlencode

import requests
import pycurl
import ssl
# import urllib.request

# from rsscast.pprint import pprint
# import youtube_dl


_LOGGER = logging.getLogger(__name__)


def read_yt_rss( yt_url ):
    try:
        buffer = BytesIO()
        session = pycurl.Curl()
        session.setopt( pycurl.URL, yt_url )
        session.setopt( pycurl.WRITEDATA, buffer)
        session.setopt( pycurl.USERAGENT, "curl/7.58.0" )
        session.setopt( pycurl.FOLLOWLOCATION, True )        ## follow redirects
        session.setopt( pycurl.CONNECTTIMEOUT, 60 )          ## connection phase timeout
#             session.setopt( pycurl.TIMEOUT, 60 )                 ## whole request timeout (transfer?)
    #         c.setopt( c.VERBOSE, 1 )
        session.perform()

        site_content = buffer.getvalue().decode('utf-8')

        return read_yt_rss_from_source( site_content )

    finally:
        session.close()

    return None


def read_yt_rss_from_source( site_content ):
    # pylint: disable=C0301
    ## <link rel="alternate" type="application/rss+xml" title="RSS" href="https://www.youtube.com/feeds/videos.xml?channel_id=UC7jDnr-ZAjQ94lf46eTcTAQ">
    match = re.search( r'<link.+?type.+?application/rss\+xml.+?href="(.+?)">', site_content )
#     match = re.search( 'link.+?type.+?application/rss\+xml.+?href.+?attribute-value.+?>(.+?)</a>', site_content )
    if not match:
        _LOGGER.warning( "unable to find link" )
#         with open("xxx.html", "w") as file1:
#             file1.write( site_content )
        return None
    foundUrl = match.group(1)

    ## <meta itemprop="name" content="namzalezy.pl">
    match = re.search( '<meta.+?itemprop.+?name.+?content="(.+?)">', site_content )
#     match = re.search( 'meta.+?itemprop.+?name.+?content.+?attribute-value.+?>(.+?)</a>', site_content )
    foundName = None
    if match:
        foundName = match.group(1)

    _LOGGER.info( "found data: %s %s", foundName, foundUrl )
    return (foundName, foundUrl)


## ===================================================================


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


def get_curl_session():
    session = pycurl.Curl()
    session.setopt( pycurl.USERAGENT, "curl/7.58.0" )
    session.setopt( pycurl.FOLLOWLOCATION, True )        ## follow redirects
    session.setopt( pycurl.CONNECTTIMEOUT, 60 )          ## connection phase timeout
#         session.setopt( pycurl.TIMEOUT, 60 )                 ## whole request timeout (transfer?)
#         c.setopt( c.VERBOSE, 1 )
    return session


def get_mp3_data( session, link, mimicHuman=True ):
#     _LOGGER.info( "curl_post: accessing %s", link )
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


## converting YT videos using webpage https://yt1s.com
def convert_yt_yt1s( link, output, mimicHuman=True ):
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

#         _LOGGER.info( "grabbing file: %s to %s", dlink, output )
        urlretrieve( dlink, output )
#         simple_download( dlink, output )
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


def urlretrieve( url, outputPath ):
    ##
    ## Under Ubuntu 20 SSL configuration has changed causing problems with SSL keys.
    ## For more details see: https://forums.raspberrypi.com/viewtopic.php?t=255167
    ##
    ctx_no_secure = ssl.create_default_context()
    ctx_no_secure.set_ciphers('HIGH:!DH:!aNULL')
    ctx_no_secure.check_hostname = False
    ctx_no_secure.verify_mode = ssl.CERT_NONE

    ## changed "user-agent" fixes blocking by server
    req = request.Request( url, headers={'User-Agent': 'Mozilla/5.0'} )
    result = request.urlopen( req, timeout=30, context=ctx_no_secure )

#     result = request.urlopen( url, context=ctx_no_secure )
    content_data = result.read()

    try:
        with open(outputPath, 'wb') as of:
            of.write( content_data )

#         content_text = content_data.decode("utf-8")
#         with open(outputPath, 'wt') as of:
#             of.write( content_text )

    except UnicodeDecodeError as ex:
        _LOGGER.exception( "unable to access: %s %s", url, ex, exc_info=False )
        raise

#     urllib.request.urlretrieve( url, outputPath, context=ctx_no_secure )
#     urllib.request.urlretrieve( url, outputPath )

    return content_data


# def simple_download( sourceUrl, outputFile ):
# #     urllib.request.urlretrieve( sourceUrl, outputFile )
# 
#     r = requests.get( sourceUrl )
#     with open( outputFile, 'wb' ) as output:
#         output.write( r.content )

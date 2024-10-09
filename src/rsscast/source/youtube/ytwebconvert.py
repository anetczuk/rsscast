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
import logging
from io import BytesIO

from urllib import request
from urllib.parse import urlencode

import ssl
import pycurl
import filetype


_LOGGER = logging.getLogger(__name__)


def get_curl_session(user_agent=None):
    session = pycurl.Curl()
    if user_agent is None:
        user_agent = "curl/7.58.0"
    session.setopt( pycurl.USERAGENT, user_agent )
    session.setopt( pycurl.FOLLOWLOCATION, True )        ## follow redirects
    session.setopt( pycurl.CONNECTTIMEOUT, 60 )          ## connection phase timeout
#         session.setopt( pycurl.TIMEOUT, 60 )                 ## whole request timeout (transfer?)
#         c.setopt( c.VERBOSE, 1 )
    session.setopt(pycurl.COOKIEJAR, '/tmp/cookie.txt')          ## save cookies to a file
    session.setopt(pycurl.COOKIEFILE, '/tmp/cookie.txt')         ## load cookies from a file
    return session


## perform 'GET' request on curl session
def curl_get( session, targetUrl, params_dict=None, header_list=None ):
#     _LOGGER.info( "accessing url: %s params: %s", targetUrl, dataDict )

    dataBuffer = BytesIO()
#     try:

    session.setopt( pycurl.POST, 0)
    if params_dict:
        session.setopt(session.URL, targetUrl + '?' + urlencode(params_dict))
    else:
        session.setopt( pycurl.URL, targetUrl )
    session.setopt( pycurl.WRITEDATA, dataBuffer )

    if header_list:
        session.setopt(pycurl.HTTPHEADER, header_list)

    session.perform()
#         except Exception as err:
#             _LOGGER.exception("Unexpected exception")
#             return ""
#     finally:
#         session.close()
    return dataBuffer


## perform 'POST' request on curl session
def curl_post( session, targetUrl, dataDict, header_list=None, verbose=False ):
#     _LOGGER.info( "accessing url: %s params: %s", targetUrl, dataDict )

    dataBuffer = BytesIO()
#     try:
    session.setopt( pycurl.URL, targetUrl )
    session.setopt( pycurl.POST, 1)
    session.setopt( pycurl.POSTFIELDS, urlencode( dataDict ))
    session.setopt( pycurl.WRITEDATA, dataBuffer )

    if header_list:
        session.setopt(pycurl.HTTPHEADER, header_list)

    if verbose:
        session.setopt(pycurl.VERBOSE, 1)
    else:
        session.setopt(pycurl.VERBOSE, 0)

    session.perform()
#         except Exception as err:
#             _LOGGER.exception("Unexpected exception")
#             return ""
#     finally:
#         session.close()
    return dataBuffer


def curl_download( session, sourceUrl, outputFile, repeatsOnFail=0 ):
    repeatsOnFail = max( repeatsOnFail, 0 )
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


def urlretrieve( url, outputPath=None, timeout=30, write_empty=True ):
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
    with request.urlopen( req, timeout=timeout, context=ctx_no_secure ) as result:

    #     result = request.urlopen( url, context=ctx_no_secure )
        content_data = result.read()

        if outputPath:
            if len(content_data) > 0 or write_empty:
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


# download URL content directly to file
def urldownload( url, outputPath=None, timeout=45):
    if not outputPath:
        return

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
    with request.urlopen( req, timeout=timeout, context=ctx_no_secure ) as result:
        file_created = False
        try:
            with open(outputPath, 'wb') as of:
                file_created = True
                CHUNK = 128 * 1024
                iteration = 0
                while True:
                    chunk = result.read(CHUNK)
                    if not chunk:
                        break
                    of.write(chunk)
                    iteration += 1
                    if iteration % 128 == 0:
                        _LOGGER.info( "in progress, already downloaded: %s MB", CHUNK * iteration / 1048576 )
        except BaseException as exc:
            _LOGGER.error( "unable to write file: %s", exc )
            if file_created:
                # exception during storage - remove incomplete file
                _LOGGER.info( "removing incomplete file: %s", outputPath )
                os.remove(outputPath)
            raise


# def simple_download( sourceUrl, outputFile ):
# #     urllib.request.urlretrieve( sourceUrl, outputFile )
#
#     r = requests.get( sourceUrl )
#     with open( outputFile, 'wb' ) as output:
#         output.write( r.content )


def check_is_mp3(output_path) -> bool:
    if os.path.isfile( output_path ) is False:
        return False

    kind = filetype.guess( output_path )
    if kind is None:
        ## server respond with HTML page instead of audio file
        os.remove( output_path )
        return False

    if kind.extension != "mp3":
        os.remove( output_path )
        return False

    return True

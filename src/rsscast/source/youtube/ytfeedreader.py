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
from io import BytesIO
import re

import pycurl


_LOGGER = logging.getLogger(__name__)


# read name and URL of RSS
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

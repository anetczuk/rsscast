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
import logging
import re
import html
from typing import List

from rsscast.rss.rssparser import RSSChannel, RSSItem
from rsscast.rss.rssparser import get_channel_output_dir
from rsscast.rss.rssparser import write_text
from rsscast.rss.ytconverter import convert_yt
from rsscast.rss.rssserver import RSSServerManager


_LOGGER = logging.getLogger(__name__)


def generate_channel_rss( feedId, rssChannel: RSSChannel, downloadContent=True ):
    host = RSSServerManager.getPrimaryIp()
    return generate_rss( host, feedId, rssChannel, downloadContent )


def generate_rss( host, feedId, rssChannel: RSSChannel, downloadContent=True ):
    items = list()
    for rssItem in rssChannel.items:
        if rssItem.enabled is False:
            continue
        items.append( rssItem )

    if downloadContent:
        download_items( feedId, items )

    return generate_items_rss( host, feedId, rssChannel, items )


def download_items( feedId, itemsList: List[RSSItem] ):
    feedId = feedId.replace(":", "_")
    feedId = re.sub( r"\s+", "", feedId )

    channelPath = get_channel_output_dir( feedId )

#     rssItem: RSSItem = None
    for rssItem in itemsList:
#         pprint( rssItem )

        postLink = rssItem.link
        videoId = rssItem.videoId()
        postLocalPath = "%s/%s.mp3" % ( channelPath, videoId )

        if not os.path.exists(postLocalPath):
            ## item file not exists -- convert and download
            _LOGGER.info( "feed %s: converting video: %s to %s", feedId, postLink, postLocalPath )
            converted = convert_yt( postLink, postLocalPath )
            if converted is False:
                ## skip elements that failed to convert
                _LOGGER.info( "feed %s: unable to convert video '%s' -- skipped", feedId, rssItem.title )
                continue

        rssItem.mediaSize = os.path.getsize( postLocalPath )


def remove_item_data( feedId, rssItem: RSSItem ):
    feedId = feedId.replace(":", "_")
    feedId = re.sub( r"\s+", "", feedId )

    channelPath = get_channel_output_dir( feedId )

    videoId = rssItem.videoId()
    postLocalPath = "%s/%s.mp3" % ( channelPath, videoId )

    rssItem.mediaSize = -1

    if not os.path.exists(postLocalPath):
        return

    os.remove( postLocalPath )


##
## podcast generation: https://feedgen.kiesow.be/
##
## download required media and generate RSS file
def generate_items_rss( host, feedId, rssChannel: RSSChannel, itemsList: List[RSSItem] ):
    feedId = feedId.replace(":", "_")
    feedId = re.sub( r"\s+", "", feedId )

    channelPath = get_channel_output_dir( feedId )

    succeed = True
    items_result = ""
#     rssItem: RSSItem = None
    for rssItem in itemsList:
#         pprint( rssItem )

        videoId = rssItem.videoId()
        postLocalPath = "%s/%s.mp3" % ( channelPath, videoId )

        if not os.path.exists(postLocalPath):
            ## item file not exists -- convert and download
            _LOGGER.info( "feed %s: unable to find video: %s", feedId, postLocalPath )
            succeed = False
            continue

        postLink = rssItem.link
        postTitle = rssItem.title

        enclosureURL = rssItem.enclosureURL( host, feedId )                           ## must have absolute path

        mediaThumbnailNode = ""
        if rssItem.thumb_url is not None:
            # pylint: disable=C0301
            mediaThumbnailNode = f"""<media:thumbnail url="{rssItem.thumb_url}" width="{rssItem.thumb_width}" height="{rssItem.thumb_height}"/>"""

        description = rssItem.summary
        description = fix_url_text( description )       ## fix URLs
        # description = html.escape( description )
        
        defaultIconURL = "http://%s/rss-icon.png" % ( host )      ## must have absolute path

        postTitle = rssItem.itemTitle()

        item_result = f"""
        <item>
            <title>{postTitle}</title>
            <link>{postLink}</link>
            <pubDate>{rssItem.publishDate}</pubDate>
            <guid>{rssItem.id}</guid>
            {mediaThumbnailNode}
            <description>{description}</description>

            <content:encoded></content:encoded>

            <enclosure url="{enclosureURL}" type="audio/mpeg" />
        </item>
"""
        items_result += item_result

    result = f"""<rss version="2.0"
 xmlns:content="http://purl.org/rss/1.0/modules/content/"
 xmlns:media="http://search.yahoo.com/mrss/"
>
    <channel>
        <title>{rssChannel.title}</title>
        <link>{rssChannel.link}</link>
        <description>YouTube channel converted to RSS by RSSCast service.</description>
        <lastBuildDate>{rssChannel.publishDate}</lastBuildDate>
        <language></language>
        <copyright></copyright>
        <image>
            <url>{defaultIconURL}</url>
            <title>{rssChannel.title}</title>
            <link>{rssChannel.link}</link>
        </image>
{items_result}
    </channel>
</rss>
"""

    rssOutput = "%s/rss" % channelPath
    _LOGGER.info( "feed %s: writing converted rss output to %s", feedId, rssOutput )
    write_text( result, rssOutput )

    return succeed


def fix_url_text( inputText ):
    outputText = inputText
    link_regex = re.compile( '((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)', re.DOTALL )
    links = re.findall( link_regex, inputText )
    for lnk in links:
        sourceURL = lnk[0]
        # print( sourceURL )
        fixedURL = fix_url( sourceURL )
        if fixedURL is None:
            continue
        outputText = outputText.replace( sourceURL, fixedURL )

    return outputText


def fix_url( inputURL ):
    """There were found invalid URL parts. It needs to be fixed to accept by AntennaPod."""
    outputURL = re.sub( r"&sub;+", "&sub", inputURL )
    outputURL = html.escape( outputURL )
    if outputURL is inputURL:
        return None
    return outputURL


# def fix_url( inputURL ):
#     """AntennaPod does not accept semicolons(;) in URLs. It can be fixed by replacing it with '&' characters."""
#     outputURL = re.sub( r";+", "&", inputURL )
#     outputURL = html.escape( outputURL )
#     if outputURL is inputURL:
#         return None
#     return outputURL

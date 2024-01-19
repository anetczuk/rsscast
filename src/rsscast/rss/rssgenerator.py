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

from rsscast.utils import write_text
from rsscast.rss.rsschannel import RSSChannel, RSSItem, get_channel_output_dir
from rsscast.rss.rssserver import RSSServerManager
from rsscast.source.youtube.ytconverter import convert_yt
from rsscast.source.youtube.ytdlpparser import is_video_available


_LOGGER = logging.getLogger(__name__)


def generate_channel_rss( feedId, rssChannel: RSSChannel, host=None, downloadContent=True, storeRSS=True ):
    """Generate channel's converted RSS."""
    if host is None:
        host = RSSServerManager.getPrimaryIp()

    if downloadContent:
        items = rssChannel.getItemsEnabled()
        duration_limit = 60 * 60 * 2        # 2 hours
        download_items( feedId, items, duration_limit )

    url_dir_path = feedId.replace(":", "_")
    url_dir_path = re.sub( r"\s+", "", url_dir_path )

    local_dir_path = get_channel_output_dir( url_dir_path )
    return generate_items_rss( rssChannel, host, url_dir_path, local_dir_path, store=storeRSS )


##
## podcast generation: https://feedgen.kiesow.be/
##
## download required media and generate RSS file
def generate_items_rss( rssChannel: RSSChannel, host, url_dir_path, local_dir_path, store=True, check_local=True ):
    """Generate channel's converted RSS content."""
    itemsList = rssChannel.getItemsEnabled()
    items_result = ""
#     rssItem: RSSItem = None
    for rssItem in itemsList:
#         pprint( rssItem )

        videoId = rssItem.videoId()
        postLocalPath = f"{local_dir_path}/{videoId}.mp3"

        if check_local:
            if not os.path.exists(postLocalPath):
                ## item file not exists -- convert and download
                _LOGGER.info( "feed %s: unable to find video: %s", url_dir_path, postLocalPath )
                continue

        enclosure_size = rssItem.localFileSize()
        if not enclosure_size or enclosure_size < 0:
            try:
                enclosure_size = os.path.getsize( postLocalPath )
            except OSError:
                enclosure_size = 0

        postLink = rssItem.link
        postTitle = rssItem.title

        enclosureURL = rssItem.getExternalURL( host, url_dir_path )              ## must have absolute path

        mediaThumbnailNode = ""
        if rssItem.thumb_url is not None:
            # pylint: disable=C0301
            width_content = ""
            if rssItem.thumb_width:
                width_content = f""" width='{rssItem.thumb_width}'"""
            height_content = ""
            if rssItem.thumb_height:
                height_content = f""" height='{rssItem.thumb_height}'"""
            mediaThumbnailNode = f"""<media:thumbnail url="{rssItem.thumb_url}"{width_content}{height_content}/>"""

        description = rssItem.summary
        description = fix_description( description )       ## fix URLs
        # description = html.escape( description )

        postTitle = rssItem.itemTitle()

        item_result = f"""
        <item>
            <title>{postTitle}</title>
            <link>{postLink}</link>
            <pubDate>{rssItem.getPublishDateRFC()}</pubDate>
            <guid>{rssItem.id}</guid>
            {mediaThumbnailNode}

            <description>{description}</description>

            <content:encoded></content:encoded>
            <enclosure url="{enclosureURL}" length="{enclosure_size}" type="audio/mpeg"/>
        </item>
"""
        items_result += item_result

    rss_url = f"http://{host}/feed/{url_dir_path}/rss"     ## must have absolute path
    defaultIconURL = f"http://{host}/rss-icon.png"          ## must have absolute path

    # <!--
    # <image>
    #   <url>https://cppcast.com/static/cppcast-logo-square.png</url>
    #   <title>CppCast</title>
    #   <link>https://cppcast.com</link>
    # </image>
    # -->

    result = f"""<rss version="2.0"
 xmlns:content="http://purl.org/rss/1.0/modules/content/"
 xmlns:media="http://search.yahoo.com/mrss/"
 xmlns:atom="http://www.w3.org/2005/Atom"
>
    <channel>
        <atom:link href="{rss_url}" rel="self" type="application/rss+xml" />
        <title>{rssChannel.title}</title>
        <link>{rssChannel.link}</link>
        <description>YouTube channel converted to RSS by RSSCast service.</description>
        <lastBuildDate>{rssChannel.getPublishDateRFC()}</lastBuildDate>
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

    if store:
        rss_local_output = f"{local_dir_path}/rss"
        _LOGGER.info( "feed %s: writing converted rss output to %s", url_dir_path, rss_local_output )
        write_text( result, rss_local_output )

    return result


## =================================================================================


# def download_items( feedId, itemsList: List[RSSItem], videoDurationLimit=None ):
def download_items( feedId, itemsList: List[RSSItem], _=None ):
    """Download media."""
    feedId = feedId.replace(":", "_")
    feedId = re.sub( r"\s+", "", feedId )

    channelPath = get_channel_output_dir( feedId )

    items_len = len(itemsList)
#     rssItem: RSSItem = None
    for index, rssItem in enumerate(itemsList):
#         pprint( rssItem )
        if rssItem.enabled is False:
            _LOGGER.info( "feed %s: video '%s' disabled -- skipped", feedId, rssItem.title )
            continue

        postLink = rssItem.link
        videoId = rssItem.videoId()
        postLocalPath = f"{channelPath}/{videoId}.mp3"

        if not os.path.exists(postLocalPath):
            ## item file not exists -- convert and download

            ## is it still needed?
            # if videoDurationLimit is not None:
            #     video_duration = get_yt_duration( postLink )
            #     if video_duration > videoDurationLimit:
            #         _LOGGER.info( "feed %s: video '%s' exceeds duration limit: %sm > %sm -- skipped",
            #                       feedId, postLink, video_duration / 60, videoDurationLimit / 60 )
            #         continue

            if not is_video_available(postLink):
                _LOGGER.warning( "feed %s: '%s' video unavailable: %s -- disabling", feedId, rssItem.title, postLink )
                rssItem.disable()
                continue

            _LOGGER.info( f"{index + 1}/{items_len} feed {feedId}:"
                          f" {rssItem.title} converting video: {postLink} to {postLocalPath}" )
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
    postLocalPath = f"{channelPath}/{videoId}.mp3"

    rssItem.mediaSize = -1

    if not os.path.exists(postLocalPath):
        return

    os.remove( postLocalPath )


def fix_description( inputText ):
    outputText = inputText
    link_regex = re.compile( r'((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)', re.DOTALL )
    links = re.findall( link_regex, inputText )
    for lnk in links:
        sourceURL = lnk[0]
        # print( sourceURL )
        fixedURL = fix_url( sourceURL )
        if fixedURL is None:
            continue
        outputText = outputText.replace( sourceURL, fixedURL )

    ## fix invalid token reported by AntennaPod
    outputText = re.sub( r" & ", " &amp; ", outputText )

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

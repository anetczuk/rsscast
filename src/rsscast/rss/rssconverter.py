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
import feedparser

from rsscast.rss.rssparser import RSSChannel
from rsscast.rss.rssparser import read_url, get_channel_output_dir
from rsscast.rss.rssparser import write_text
from rsscast.rss.ytconverter import convert_yt


_LOGGER = logging.getLogger(__name__)


##
## podcast generation: https://feedgen.kiesow.be/
##
def convert_rss( host, feedId, feedUrl ):
    _LOGGER.info( "feed %s: reading url %s", feedId, feedUrl )
    feedContent = read_url( feedUrl )
    channelPath = get_channel_output_dir( feedId )
    sourceRSS = os.path.abspath( os.path.join(channelPath, "source.rss") )
    write_text( feedContent, sourceRSS )
    
    _LOGGER.info( "feed %s: parsing rss", feedId )
    parsedDict = feedparser.parse( feedContent )

    _LOGGER.info( "feed %s: detected entries %s", feedId, len(parsedDict.entries) )
#     pprint( parsedDict.feed )
#     pprint( parsedDict.entries )

    rssChannel = RSSChannel()
    rssChannel.parse( feedContent )
    generate_content( host, feedId, rssChannel )


def generate_content( host, feedId, rssChannel: RSSChannel ):
    feedId = feedId.replace(":", "_")
    feedId = re.sub( r"\s+", "", feedId )

    channelPath = get_channel_output_dir( feedId )

    items_result = ""
#     rssItem: RSSItem = None
    for rssItem in rssChannel.items:
#         pprint( rssItem )

        videoId = rssItem.videoId()
        postLink = rssItem.link
        postLocalPath = "%s/%s.mp3" % ( channelPath, videoId )
        postTitle = rssItem.title

        if not os.path.exists(postLocalPath):
            ## item file not exists -- convert and download
            converted = convert_yt( postLink, postLocalPath )
            if converted is False:
                ## skip elements that failed to convert
                _LOGGER.info( "feed %s: unable to convert video '%s' -- skipped", feedId, postTitle )
                continue
        else:
            _LOGGER.info( "feed %s: local conversion of %s found in %s", feedId, postLink, postLocalPath )

        enclosureURL  = "http://%s/feed/%s/%s.mp3" % ( host, feedId, videoId )      ## must have absolute path

        mediaThumbnailNode = ""
        if rssItem.thumb_url is not None:
            # pylint: disable=C0301
            mediaThumbnailNode = f"""<media:thumbnail url="{rssItem.thumb_url}" width="{rssItem.thumb_width}" height="{rssItem.thumb_height}"/>"""

        description = rssItem.summary
        # description = html.escape( description )

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
        <description></description>
        <lastBuildDate>{rssChannel.publishDate}</lastBuildDate>
        <language></language>
        <copyright></copyright>
        <image>
            <url></url>
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

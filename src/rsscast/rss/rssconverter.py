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
import requests
import requests_file
import feedparser

from rsscast import DATA_DIR
from rsscast.rss.ytconverter import convert_yt


_LOGGER = logging.getLogger(__name__)


##
## podcast generation: https://feedgen.kiesow.be/
##
def convert_rss( host, feedId, feedUrl ):
    _LOGGER.info( "feed %s: reading url %s", feedId, feedUrl )
    content = read_url( feedUrl )
    channelPath = get_channel_output_dir( feedId )
    sourceRSS = os.path.abspath( os.path.join(channelPath, "source.rss") )
    write_text( content, sourceRSS )
    convert_rss_content( host, feedId, content )


def convert_rss_content( host, feedId, feedContent ):
    _LOGGER.info( "feed %s: parsing rss", feedId )
    parsedDict = feedparser.parse( feedContent )

    _LOGGER.info( "feed %s: detected entries %s", feedId, len(parsedDict.entries) )
#     pprint( parsedDict.feed )
#     pprint( parsedDict.entries )

    feedId = feedId.replace(":", "_")
    feedId = re.sub( r"\s+", "", feedId )

    channelPath = get_channel_output_dir( feedId )

    items_result = ""
    for post in parsedDict.entries:
#         pprint( post )

#         videoId = post['yt_videoid']
        videoId = post['id']
        videoId = videoId.replace(":", "_")
        postLink = post['link']
        postLocalPath = "%s/%s.mp3" % ( channelPath, videoId )
        enclosureURL  = "http://%s/feed/%s/%s.mp3" % ( host, feedId, videoId )      ## must have absolute path
        postTitle = post['title']
        postTitle = html.escape( postTitle )

        if not os.path.exists(postLocalPath):
            converted = convert_yt( postLink, postLocalPath )
            if converted is False:
                ## skip elements that failed to convert
                _LOGGER.info( "feed %s: unable to convert video '%s' -- skipped", feedId, postTitle )
                continue
        else:
            _LOGGER.info( "feed %s: local conversion of %s found in %s", feedId, postLink, postLocalPath )

        mediaThumbnailNode = ""
        if 'media_thumbnail' in post:
            thumbnail = post['media_thumbnail'][0]
            # pylint: disable=C0301
            mediaThumbnailNode = f"""<media:thumbnail url="{thumbnail['url']}" width="{thumbnail['width']}" height="{thumbnail['height']}"/>"""

        description = post.get('summary', '')
        # description = html.escape( description )

        item_result = f"""
        <item>
            <title>{postTitle}</title>
            <link>{post['link']}</link>
            <pubDate>{post['published']}</pubDate>
            <guid>{post['id']}</guid>
            {mediaThumbnailNode}
            <description>{description}</description>

            <content:encoded></content:encoded>

            <enclosure url="{enclosureURL}" type="audio/mpeg" />
        </item>
"""
        items_result += item_result

#     rssData = dict()
#     rssData['rss_feed_title'] = parsedDict['feed']['title']
#    ## example: """{rss_feed_title}""".format( **rssData )

    parsedFeed = parsedDict['feed']
    feedLink = parsedFeed.get('href', "")
    feedPublished = parsedFeed.get('published', "")

    result = f"""<rss version="2.0"
 xmlns:content="http://purl.org/rss/1.0/modules/content/"
 xmlns:media="http://search.yahoo.com/mrss/"
>
    <channel>
        <title>{parsedFeed['title']}</title>
        <link>{feedLink}</link>
        <description></description>
        <lastBuildDate>{feedPublished}</lastBuildDate>
        <language></language>
        <copyright></copyright>
        <image>
            <url></url>
            <title>{parsedFeed['title']}</title>
            <link>{feedLink}</link>
        </image>
{items_result}
    </channel>
</rss>
"""

    rssOutput = "%s/rss" % channelPath
    _LOGGER.info( "feed %s: writing converted rss output to %s", feedId, rssOutput )
    write_text( result, rssOutput )


def read_url( urlpath ):
    session = requests.Session()
    session.mount( 'file://', requests_file.FileAdapter() )
#     session.config['keep_alive'] = False
#     response = requests.get( urlpath, timeout=5 )
    response = session.get( urlpath, timeout=5 )
#     response = requests.get( urlpath, timeout=5, hooks={'response': print_url} )
    return response.text


def get_channel_output_dir( feedId ):
    channelPath = os.path.abspath( os.path.join(DATA_DIR, "feed", feedId) )
    os.makedirs( channelPath, exist_ok=True )
    return channelPath


def write_text( content, outputPath ):
    with open( outputPath, 'wt' ) as fp:
        fp.write( content )

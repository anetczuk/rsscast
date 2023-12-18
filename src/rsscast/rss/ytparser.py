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
import datetime

# import pprint

from email import utils
from xml.sax.saxutils import escape
import requests

from yt_dlp import YoutubeDL

from rsscast.rss.rssparser import RSSChannel, parse_rss


_LOGGER = logging.getLogger(__name__)


## ============================================================


def parse_url( feedId, feedUrl, full_list=False, write_content=True ) -> RSSChannel:
    # 'parse_rss' for backward compatibility
    channel = parse_rss(feedId, feedUrl, write_content)
    if channel:
        return channel
    if full_list:
        channel = parse_playlist_raw(feedUrl, items_num=9999)
    else:
        channel = parse_playlist_raw(feedUrl)
    if channel:
        return channel
    # no data found
    return RSSChannel()


def parse_playlist_raw( video_url, items_num=15 ) -> RSSChannel:
    _LOGGER.info( "feed raw parsing url %s", video_url )

    info_dict = fetch_info(video_url, items_num)
    reduce_info(info_dict)

    return convert_info_to_channel(info_dict)


def parse_playlist_lazy( video_url, known_items=None ) -> RSSChannel:
    _LOGGER.info( "feed lazy parsing url %s", video_url )

    if not known_items:
        known_items = set()

    info_dict = fetch_info(video_url, items_num=9999, process=False)

    entries_list = []
    entries_gen = info_dict.get("entries")
    for item in entries_gen:
        yt_link = item.get("url", "")
        if not yt_link or yt_link in known_items:
            _LOGGER.info("skipping known url: %s", yt_link)
            continue
        # _LOGGER.info("fetching video: %s", yt_link)
        vid_info_dict = fetch_info(yt_link, items_num=999, process=False)
        entries_list.append(vid_info_dict)

    info_dict["entries"] = entries_list
    reduce_info(info_dict)

    return convert_info_to_channel(info_dict)


def convert_info_to_channel(info_dict) -> RSSChannel:
    channel_modified_date = info_dict.get("modified_date")
    data_feed = {
        "title": info_dict.get("title"),
        "href": info_dict.get("channel_url"),
        "published": num_date_to_datetime(channel_modified_date)
    }

    data_entries = []

    yt_entries = info_dict.get('entries', [])
    for yt_entry in yt_entries:
        yt_link = yt_entry.get("original_url", "")
        # yt_link = yt_entry.get("original_url", "")
        if not yt_link:
            continue
        yt_id = yt_entry["id"]
        thumb_dict = get_thumbnail_data(yt_entry)
        item_upload_date = yt_entry.get("upload_date")
        item = {
            "id": f"yt:video:{yt_id}",
            "title": yt_entry.get("title", ""),
            "link": yt_link,
            "media_thumbnail": thumb_dict,
            "summary": yt_entry.get("description", ""),
            "published": num_date_to_datetime(item_upload_date)
        }
        data_entries.append(item)

    feedContent = {
        "feed": data_feed,
        "entries": data_entries
    }

    # pprint.pprint(info_dict)
    # pprint.pprint(feedContent)

    _LOGGER.info( "feed parsing done" )
    _LOGGER.info( "adding feed items" )

    rssChannel = RSSChannel()
    if not rssChannel.parseData( feedContent ):
        # unable to parse
        return None
    return rssChannel


# order of items in list seems to be random
def fetch_info(video_url, items_num=15, process=True):
    params = {"skip_download": True,
              "playlist_items": f"1:{items_num}",
              ## restricting player_client causes longer duration of 'extract_info'
              # "extractor_args": {"youtube": {
              #                           "player_client": ["web"]
              #                       }
              #                    }
              }

    with YoutubeDL(params) as ydl:
        info_dict = ydl.extract_info(video_url, download=False, process=process)

    return info_dict


def reduce_info(info_dict):
    entries = info_dict.get("entries", [])
    for item in entries:
        reduce_entry_info(item)


def reduce_entry_info(item):
    if "automatic_captions" in item:
        item["automatic_captions"] = "automatic_captions_reduced"
    if "formats" in item:
        item["formats"] = "formats_removed"
    if "requested_formats" in item:
        item["requested_formats"] = "requested_formats_reduced"
    if "subtitles" in item:
        item["subtitles"] = "subtitles_formats_reduced"
    if "tags" in item:
        item["tags"] = "tags_reduced"


# output format: '2014-05-24T20:50:40+00:00'
def epoch_to_datetime(epoch_value):
    date_time = datetime.datetime.fromtimestamp(epoch_value, tz=datetime.timezone.utc)
    return date_time.isoformat()


# input format: '20171027'
# output must be an RFC-822 date-time
# output format: 'Wed, 02 Oct 2002 15:00:00 +0200'
def num_date_to_datetime(num_date):
    date_time = datetime.datetime.strptime(num_date, "%Y%m%d")
    return utils.format_datetime(date_time)
    # return date_time.isoformat()


def get_thumbnail_data(yt_entry):
    thumb_url = yt_entry.get("thumbnail")
    if thumb_url:
        thumb_url = escape(thumb_url)       # escape XML special characters like <, > and &
        ret_dict = {
            "url": thumb_url
        }
        return [ret_dict]

    thumbs_list = yt_entry.get("thumbnails", [])
    if thumbs_list:
        thumb_item = thumbs_list[-1]
        ret_dict["url"] = thumb_item.get("url")
        ret_dict["width"] = thumb_item.get("width")
        ret_dict["height"] = thumb_item.get("height")

    return [ret_dict]


def check_url(thumb_url):
    if not thumb_url:
        return thumb_url
    try:
        headers = {
            'User-Agent': 'My User Agent 1.0'
        }
        response = requests.head(thumb_url, timeout=15, headers=headers, allow_redirects=True)
        # _LOGGER.info("link %s response code: %s", url, response.status_code)
        if response.status_code == 200:
            return thumb_url
        return None
    except requests.exceptions.ConnectionError:
        return None

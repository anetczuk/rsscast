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
        channel = parse_playlist(feedId, feedUrl, items_num=9999)
    else:
        channel = parse_playlist(feedId, feedUrl)
    if channel:
        return channel
    # no data found
    return RSSChannel()


def parse_playlist( feedId, video_url, items_num=15 ) -> RSSChannel:
    _LOGGER.info( "feed %s: reading url %s", feedId, video_url )

    info_dict = fetch_info(video_url, items_num)
    
    # import pprint
    # # pprint.pprint(info_dict)
    #
    # entries_list = []
    # for item in info_dict.get("entries"):
    #     yt_link = item.get("url", "")
    #     if not yt_link:
    #         continue
    #     with YoutubeDL(params) as ydl:
    #         vid_info_dict = ydl.extract_info(yt_link, download=False, process=False)
    #     entries_list.append(vid_info_dict)
    # info_dict["entries"] = entries_list
    #
    # pprint.pprint(info_dict)

    channel_modified_date = info_dict.get("modified_date")
    data_feed = {
        "title": info_dict.get("title"),
        "href": info_dict.get("channel_url"),
        "published": num_date_to_date(channel_modified_date)
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
            "published": num_date_to_date(item_upload_date)
        }
        data_entries.append(item)

    feedContent = {
        "feed": data_feed,
        "entries": data_entries
    }

    # pprint.pprint(info_dict)
    # pprint.pprint(feedContent)

    rssChannel = RSSChannel()
    if not rssChannel.parseData( feedContent ):
        # unable to parse
        return None
    _LOGGER.info( "feed %s: parsing done", feedId )
    return rssChannel


def fetch_info(video_url, items_num=15):
    params = {"skip_download": True,
              "playlist_items": f"1:{items_num}"}

    with YoutubeDL(params) as ydl:
        info_dict = ydl.extract_info(video_url, download=False, process=True)
        # info_dict = ydl.extract_info(video_url, download=False, process=False)
        return info_dict


# output format: '2014-05-24T20:50:40+00:00'
def epoch_to_datetime(epoch_value):
    date_time = datetime.datetime.fromtimestamp(epoch_value, tz=datetime.timezone.utc)
    return date_time.isoformat()


# input format: '20171027'
# output format: '2014-05-24'
def num_date_to_date(num_date):
    date_time = datetime.datetime.strptime(num_date, "%Y%m%d")
    return date_time.date().isoformat()


def get_thumbnail_data(yt_entry):
    # thumb_url = yt_entry.get("thumbnail")
    # if not thumb_url:
    #     return [{}]
    # ret_dict = {
    #     "url": thumb_url
    # }

    ret_dict = {}

    # thumbs_list = yt_entry.get("thumbnails", [])
    # for thumb_item in reversed(thumbs_list):
    #     thumb_url = thumb_item.get("url")
    #     thumb_url = check_url(thumb_url)
    #     if not thumb_url:
    #         continue
    #
    #     ret_dict["url"] = thumb_url
    #
    #     width = thumb_item.get('width')
    #     if width:
    #         ret_dict["width"] = width
    #     height = thumb_item.get('height')
    #     if height:
    #         ret_dict["height"] = height
    #
    #     # found valid thumbnail
    #     break

    thumbs_list = yt_entry.get("thumbnails", [])
    if thumbs_list:
        thumb_item = thumbs_list[-1]
        ret_dict["url"] = thumb_item.get("url")
        ret_dict["width"] = thumb_item.get("width")
        ret_dict["height"] = thumb_item.get("height")

    # for thumb_item in thumbs_list:
    #     if thumb_item["url"] == thumb_url:
    #         ret_dict["width"] = thumb_item.get("width", "")
    #         ret_dict["height"] = thumb_item.get("height", "")
    #         break

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

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
import datetime
from enum import Enum, unique, auto
from typing import List, Dict, Any

from xml.sax.saxutils import escape
import requests

import yt_dlp

from rsscast.rss.rsschannel import RSSChannel
# from pydub.audio_segment import AudioSegment


_LOGGER = logging.getLogger(__name__)


# # set loglevel of library
# l = logging.getLogger("pydub.converter")
# l.setLevel(logging.WARNING)


## ============================================================


def convert_yt( link, output, _mimicHuman=True, format_id=None ) -> bool:
    _LOGGER.info("yt_dlp: converting youtube video %s", link)

    if format_id is None:
        # 'format': '140'
        # 'format': 'bestaudio'
        # format_id = 'bestaudio/best'
        format_id = "bestaudio"

    yt_path = output
    yt_path = yt_path.rstrip(".mp3")
    # yt_path = f"{output_path}.yt_audio"

    try:
        # AntennaPod does not like mp4 files (it is unable to fast-forward or play from certain time)
        ydl_opts = {'extract_audio': True,
                    'outtmpl': yt_path,
                    'format': format_id,
                    "logger": YTDLPLogger,
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '128',
                    }]
                    }

        with yt_dlp.YoutubeDL(ydl_opts) as video:
            video.download(link)

    except yt_dlp.utils.DownloadError:
        # error already reported by YTDLPLogger
        if os.path.isfile(yt_path):
            _LOGGER.info( "removing incomplete file: %s", yt_path )
            # exception during storage - remove incomplete file
            os.remove(yt_path)
        return False

    except BaseException as exc:
        _LOGGER.error("error during download of audio: %s", exc)
        if os.path.isfile(yt_path):
            _LOGGER.info( "removing incomplete file: %s", yt_path )
            # exception during storage - remove incomplete file
            os.remove(yt_path)
        return False

    ## kills application because of memory consumption
    # _LOGGER.info("converting YT audio to mp3")
    # # AntennaPod does not like mp4 files (it is unable to fast-forward or play from certain time)
    # # convert in place
    # AudioSegment.from_file(yt_path).export(output_path, format="mp3", bitrate="128k")

    _LOGGER.info("downloading completed")
    return True


## ============================================================


def parse_playlist( page_url, known_items=None, max_fetch=10 ) -> RSSChannel:
    info_dict = parse_playlist_data(page_url, known_items, max_fetch)
    return convert_info_to_channel(info_dict)


def parse_playlist_data( page_url, known_items=None, max_fetch=10 ) -> Dict[Any, Any]:
    _LOGGER.info( "parsing youtube playlist url %s", page_url )

    if not known_items:
        known_items = set()

    info_dict = fetch_info(page_url, items_num=999999)
    if info_dict is None:
        return None

    if max_fetch > 0:
        _LOGGER.info( "fetching youtube videos" )
        fetch_count = 0
        entries_list = []
        entries_gen = info_dict.get("entries")

        i = 0
        while i < len(entries_gen):
            if fetch_count >= max_fetch:
                _LOGGER.info("max items fetch reached[%s], breaking", max_fetch)
                break

            item = entries_gen[i]
            i += 1

            yt_link = item.get("url", "")
            if not yt_link or yt_link in known_items:
                _LOGGER.info("skipping known url: %s", yt_link)
                continue

            fetch_count += 1

            _LOGGER.info("%s of %s: fetching youtube url: %s", i, len(entries_gen), yt_link)
            sub_info_dict = fetch_info(yt_link, items_num=999)
            if sub_info_dict is None:
                # error while getting info
                sub_info_dict = {"link": yt_link}
                entries_list.append(sub_info_dict)
                continue

            sub_items = sub_info_dict.get("entries")
            if sub_items is not None:
                # sublist case - append to current list
                fetch_count -= 1        # reduce - fetch indicates number of videos
                _LOGGER.info("%s of %s: found sublist items %s", i, len(entries_gen), len(sub_items))
                new_list: List[str] = []
                new_list.extend( entries_gen[0:i - 1] )
                new_list.extend( sub_items )
                new_list.extend( entries_gen[i:] )
                entries_gen = new_list
                continue

            entries_list.append(sub_info_dict)

        info_dict["entries"] = entries_list

    # import pprint
    # pprint.pprint(info_dict)

    return info_dict


def convert_info_to_channel(info_dict) -> RSSChannel:
    # channel_modified_date = info_dict.get("modified_date")
    # published_date = num_date_to_datetime(channel_modified_date)

    epoch_date = info_dict.get("epoch")
    published_date = epoch_to_datetime(epoch_date)

    data_feed = {
        "title": info_dict.get("title"),
        "href": info_dict.get("channel_url"),
        "published": published_date
    }

    data_entries = []

    yt_entries = info_dict.get('entries', [])
    for yt_entry in yt_entries:
        yt_link = yt_entry.get("url", "")
        if not yt_link:
            yt_link = yt_entry.get("original_url", "")
        if not yt_link:
            # it happens for private videos
            _LOGGER.warning("unable to add item to channel (no ID), entries:\n%s", yt_entries)
            continue
        yt_id = yt_entry["id"]
        thumb_dict = get_thumbnail_data(yt_entry)
        item_upload_date = yt_entry.get("upload_date")

        summary_data = yt_entry.get("description", "")
        # if summary_data is None:
        #     entry_format = pprint.pformat(yt_entry, indent=4)
        #     _LOGGER.warning("unable to get summary from link %s from entry:\n%s", yt_link, entry_format)

        published_data = num_date_to_datetime(item_upload_date)
        if published_data is None:
            epoch_date = yt_entry.get("epoch")
            published_data = epoch_to_datetime(epoch_date)

        item = {
            "id": f"yt:video:{yt_id}",
            "title": yt_entry.get("title", ""),
            "link": yt_link,
            "media_thumbnail": thumb_dict,
            "summary": summary_data,
            "published": published_data
        }
        data_entries.append(item)

    feedContent = {
        "feed": data_feed,
        "entries": data_entries
    }

    # pprint.pprint(info_dict)
    # pprint.pprint(feedContent)

    _LOGGER.info( "feed parsing done" )
    _LOGGER.info( "adding feed items %s", len(data_entries) )

    rssChannel = RSSChannel()
    rssChannel.parseData( feedContent )
    return rssChannel


@unique
class VideoAvailableStatus(Enum):
    OK        = auto()  # video available
    UPCOMING  = auto()  # video still not available
    INVALID   = auto()  # some error


def is_video_available(video_url) -> VideoAvailableStatus:
    result = fetch_info(video_url)
    if result is None:
        return VideoAvailableStatus.INVALID

    live_status = result.get("live_status")
    if live_status is None:
        return VideoAvailableStatus.INVALID

    if live_status in ("not_live", "was_live"):
        return VideoAvailableStatus.OK

    if live_status == "is_upcoming":
        return VideoAvailableStatus.UPCOMING

    _LOGGER.warning("unhandled live status: %s", live_status)
    return VideoAvailableStatus.UPCOMING


def list_audio_formats(video_url):
    info_dict = fetch_info(video_url, reduce=False)
    foramts = info_dict.get("formats", [])

    ret_list = []
    for item in foramts:
        if item.get("audio_ext", "none") == "none":
            continue
        data = item.copy()
        data['fragments'] = "<removed>"
        data['fragment_base_url'] = "<removed>"
        data['http_headers'] = "<removed>"
        data['manifest_url'] = "<removed>"
        data['url'] = "<removed>"
        ret_list.append(data)

    return ret_list


class YTDLPLogger:

    @staticmethod
    def error(msg):
        if "Private video" in msg:
            _LOGGER.info(msg)
            return
        if "Premieres in " in msg:
            _LOGGER.info(msg)
            return
        _LOGGER.error(msg)

    @staticmethod
    def warning(msg):
        if "nsig extraction failed: You may experience throttling for some formats" in msg:
            _LOGGER.info(msg)
            return
        if "Incomplete data received. Retrying" in msg:
            _LOGGER.info(msg)
            return
        if "Incomplete data received. Giving up after" in msg:
            _LOGGER.info(msg)
            return
        if "unavailable video is hidden" in msg:
            _LOGGER.info(msg)
            return
        if "Video unavailable. This video has been removed by the uploader" in msg:
            _LOGGER.info(msg)
            return
        _LOGGER.warning(msg)

    @staticmethod
    def debug(msg):
        _LOGGER.debug(msg)


# order of items in list seems to be random
# youtube_url can be URL to channel or playlist or URL to video
# returns None if failed/invalid url/video not available
def fetch_info(youtube_url, items_num=15, reduce=True):
    params = {"skip_download": True,
              "simulate": True,
              "ignore_no_formats_error": True,
              "extract_flat": True,                     # do not download videos from list
              # "dump_single_json": True,                ## will print JSON to stdout
              "playlist_items": f"1:{items_num}",
              # "playlistreverse": True,                # reverses all items (videos and playlists)
              "logger": YTDLPLogger,

              ## restricting player_client causes longer duration of 'extract_info'
              # "extractor_args": {"youtube": {
              #                           "player_client": ["web"]
              #                       }
              #                    }
              }

    try:
        with yt_dlp.YoutubeDL(params) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=False)

        if info_dict is None:
            _LOGGER.warning("unable to fetch info from url: %s", youtube_url)

    except yt_dlp.utils.DownloadError:
        # error already reported by YTDLPLogger
        _LOGGER.error("unable to download %s", youtube_url)
        return None

    if reduce:
        reduce_info(info_dict)

    # item_type = info_dict.get('_type', "")        # applies to videos and playlists

    # 'webpage_url_basename': 'playlist',
    item_type = info_dict.get('webpage_url_basename', "")   # eg. "playlist" or "videos"
    if item_type == 'playlist':
        # playlist
        entries = info_dict.get("entries")
        if entries:
            _LOGGER.info("playlist detected - reversing entries")
            entries.reverse()
            info_dict["entries"] = entries

    return info_dict


def reduce_info(info_dict):
    entries = info_dict.get("entries", [])
    for item in entries:
        reduce_entry_info(item)
    reduce_entry_info(info_dict)


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


# output string, in format '2014-05-24T20:50:40+00:00'
def epoch_to_datetime(epoch_value):
    date_time = datetime.datetime.fromtimestamp(epoch_value, tz=datetime.timezone.utc)
    return date_time.isoformat()


# input format: '20171027'
# output string, in format '2014-05-24T20:50:40+00:00'
def num_date_to_datetime(num_date):
    if num_date is None:
        return None
    date_time = datetime.datetime.strptime(num_date, "%Y%m%d")
    date_time = date_time.replace(tzinfo=datetime.timezone.utc)
    # return utils.format_datetime(date_time)
    return date_time.isoformat()


def get_thumbnail_data(yt_entry):
    thumb_url = yt_entry.get("thumbnail")
    if thumb_url:
        thumb_url = escape(thumb_url)       # escape XML special characters like <, > and &
        ret_dict = {
            "url": thumb_url
        }
        return [ret_dict]

    ret_dict = {}
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

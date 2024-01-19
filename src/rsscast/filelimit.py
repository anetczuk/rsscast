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
from typing import List
import datetime

from rsscast.rss.rsschannel import RSSItem
from rsscast.datatypes import FeedEntry


_LOGGER = logging.getLogger(__name__)


def remove_old_files(feedList: List[ FeedEntry ], files_limit):
    files_list = get_files_list(feedList)
    files_no = len(files_list)
    rem_num = files_no - files_limit
    if rem_num < 1:
        _LOGGER.info("nothing to remove - files limit not reached [%s <= %s]", files_no, files_limit)
        return False

    files_to_remove = files_list[:rem_num]
    for item in files_to_remove:
        dt_object = item[0]
        feed: FeedEntry = item[2]
        rss_item: RSSItem = item[3]
        rss_item.disable()
        file_path = item[1]
        _LOGGER.info("removing file %s: %s %s %s", feed.feedId, rss_item.title, file_path, dt_object)
        os.remove(file_path)
    return True


def get_files_list(feedList: List[ FeedEntry ]):
    files_list = []
    for feed in feedList:
        local_paths = feed.getLocalPaths()
        for rss_item, file_path in local_paths:
            try:
                mod_time = os.path.getmtime( file_path )
                dt_object = datetime.datetime.fromtimestamp(mod_time)
                files_list.append( (dt_object, file_path, feed, rss_item) )
            except FileNotFoundError:
                continue
    files_list.sort()
    return files_list

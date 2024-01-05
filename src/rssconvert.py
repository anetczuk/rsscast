#!/usr/bin/python3
#
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

import sys
import os
import logging
import argparse

import json

from rsscast import logger
from rsscast.rss.rssparser import RSSChannel
from rsscast.rss.rssconverter import generate_items_rss
from rsscast.rss.ytparser import reduce_info, convert_info_to_channel


_LOGGER = logging.getLogger(__name__)


def process_ytrss(args):
    input_file_path = args.infile
    output_dir_path = args.outdir

    with open(input_file_path, 'rt', encoding="utf-8") as in_file:
        input_data = in_file.read()

    rssChannel = RSSChannel()
    if not rssChannel.parseRSS( input_data ):
        # unable to parse
        return
    write_channel_rss(rssChannel, output_dir_path)


def process_ytdlp(args):
    input_file_path = args.infile
    output_dir_path = args.outdir

    with open(input_file_path, 'rt', encoding="utf-8") as in_file:
        info_dict = json.load(in_file)

    reduce_info(info_dict)
    rssChannel: RSSChannel = convert_info_to_channel(info_dict)
    write_channel_rss(rssChannel, output_dir_path)


## =======================================================================================================


def write_channel_rss(rssChannel, output_dir_path):
    os.makedirs(output_dir_path, exist_ok=True )
    items = rssChannel.items
    generate_items_rss( rssChannel, items, "rsshost", "feed_dir", output_dir_path, store=True, check_local=False )


## =======================================================================================================


def main():
    parser = argparse.ArgumentParser(description="convert data to RSS")
    parser.add_argument("--listtools", action="store_true", help="List tools")
    parser.set_defaults(func=None)

    subparsers = parser.add_subparsers(help="one of tools", description="use one of tools", dest="tool", required=False)

    ## =================================================

    description = "convert YouTube RSS"
    subparser = subparsers.add_parser("ytrss", help=description)
    subparser.description = description
    subparser.set_defaults(func=process_ytrss)
    subparser.add_argument(
        "--infile",
        action="store",
        required=False,
        default="",
        help="Input file containing YouTube RSS",
    )
    subparser.add_argument(
        "--outdir",
        action="store",
        required=False,
        default="",
        help="Output dir to store converted RSS",
    )

    ## =================================================

    description = "convert output of yt-dlp library"
    subparser = subparsers.add_parser("ytdlp", help=description)
    subparser.description = description
    subparser.set_defaults(func=process_ytdlp)
    subparser.add_argument(
        "--infile",
        action="store",
        required=False,
        default="",
        help="Input file containing yt-dlp info dict",
    )
    subparser.add_argument(
        "--outdir",
        action="store",
        required=False,
        default="",
        help="Output dir to store converted RSS",
    )

    ## =================================================

    args = parser.parse_args()

    if args.listtools is True:
        tools_list = list(subparsers.choices.keys())
        print(", ".join(tools_list))
        return 0

    if not args.func:
        ## no command given -- print help message
        parser.print_help()
        sys.exit(1)
        return 1

    logger.configure()

    args.func(args)

    return 0


if __name__ == '__main__':
    main()

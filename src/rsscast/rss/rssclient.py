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
import feedparser
import time
import urllib.request
import requests
import logging
from rsscast.pprint import pprint
import requests_file



script_dir = os.path.dirname(os.path.realpath(__file__))

tmp_dir = os.path.abspath( script_dir + "/../../../tmp/" ) + "/"



# logging.basicConfig(level=logging.DEBUG)


# def print_url(r, *args, **kwargs):
#     print(r.url)


def read_url( urlpath ):
    session = requests.Session()
    session.mount( 'file://', requests_file.FileAdapter() )
#     session.config['keep_alive'] = False
#     response = requests.get( urlpath, timeout=5 )
    response = session.get( urlpath, timeout=5 )
#     response = requests.get( urlpath, timeout=5, hooks={'response': print_url} )
    return response.text


def read_rss( urlpath ):
    session = requests.Session()
    session.mount( 'file://', requests_file.FileAdapter() )
#     session.config['keep_alive'] = False
#     response = requests.get( urlpath, timeout=5 )
    response = session.get( urlpath, timeout=5 )
#     response = requests.get( urlpath, timeout=5, hooks={'response': print_url} )
#     print("xxxxxxxx1\n>%s<" % response.text)

    parse_rss( response.text )


# #     req = urllib.request.Request(
# #         urlpath,
# #         data=None,
# #         headers={
# #             'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
# #         }
# #     )
#
#
# #     req = urllib.request.Request(urlpath, headers={'User-Agent': 'Mozilla/5.0'})
# #
# # #     with urllib.request.urlopen(req, timeout=10) as response:
# #     with urllib.request.urlopen(req) as response:
# #         print("xxxxxxxx1")
# # #         html = response.read()
# # #         print("xxxxxxxx2", html)
# #         return
#
#
# #     urllib.request.urlretrieve( urlpath, "aaa.txt" )
# #     print("xxxxxxxx0-a:", urlpath)
# #     with urllib.request.urlopen(    urlpath,
# #                                     data=None
# # #                                     ,
# # #                                     headers={
# # #                                         'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
# # #                                     }
# #                                 ) as response:
# #         print("xxxxxxxx1")
# #         html = response.read()
# #         print("xxxxxxxx2", html)
# #         return
#     d = feedparser.parse('http://chicagotribune.feedsportal.com/c/34253/f/622872/index.rss')
#     d = feedparser.parse( 'https://www.nasa.gov/rss/dyn/lg_image_of_the_day.rss' )
#     d = feedparser.parse( 'https://blogs.nasa.gov/stationreport/feed/' )


def parse_rss( content ):
    parsedDict = feedparser.parse( content )

#     print("xxxxxxx\n", parsedDict['feed']['title'] )

#     pprint( parsedDict )
#     pprint( parsedDict.entries )

    ## print all posts
#     count = 1
#     blockcount = 1
    for post in parsedDict.entries:
#         if count % 5 == 1:
#             print( "\n" + time.strftime("%a, %b %d %I:%M %p") + '  ((( TRIBUNE - ' + str(blockcount) + ' )))' )
#             print( "-----------------------------------------\n" )
#             blockcount += 1
        print( "%s\n\t%s" % (post.title, post.link) )
#         count += 1

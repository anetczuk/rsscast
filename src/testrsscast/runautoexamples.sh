#!/bin/bash

set -eux

## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


## synchronous example 
#$SCRIPT_DIR/gui/mainwindow_example.py

## synchronous example 
#$SCRIPT_DIR/gui/widget/logwindow_example.py

$SCRIPT_DIR/rss/rssgenerator_example.py

## synchronous example 
#$SCRIPT_DIR/rss/rssserver_example.py

## does not check automatically
#$SCRIPT_DIR/source/parser_example.py


$SCRIPT_DIR/source/youtube/convert_ddownr_com_example.py

## does not work
#$SCRIPT_DIR/source/youtube/convert_publer_io_example.py

$SCRIPT_DIR/source/youtube/convert_pytube_example.py

$SCRIPT_DIR/source/youtube/convert_y2down_cc_example.py

$SCRIPT_DIR/source/youtube/convert_youtube_dl_example.py

$SCRIPT_DIR/source/youtube/convert_yt_dlp_example.py
$SCRIPT_DIR/source/youtube/convert_yt_dlp_featured_example.py
$SCRIPT_DIR/source/youtube/convert_yt_dlp_playlist_example.py
$SCRIPT_DIR/source/youtube/convert_yt_dlp_video_example.py
$SCRIPT_DIR/source/youtube/convert_yt_dlp_videos_example.py

$SCRIPT_DIR/source/youtube/convert_yt1s_com_example.py

$SCRIPT_DIR/source/youtube/ytconverter_example.py

## unfinished
#$SCRIPT_DIR/source/youtube/selenium_example.py

$SCRIPT_DIR/integration/intgr_ytconverter.py

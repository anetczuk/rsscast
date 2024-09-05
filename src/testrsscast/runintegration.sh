#!/bin/bash

set -eux

## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


$SCRIPT_DIR/source/intgr_parser.py


$SCRIPT_DIR/source/youtube/intgr_convert_ddownr_com.py

## does not work
#$SCRIPT_DIR/source/youtube/intgr_convert_publer_io.py

## conversion from mp4 to mp3 needed
# $SCRIPT_DIR/source/youtube/intgr_convert_pytube.py

$SCRIPT_DIR/source/youtube/intgr_convert_y2down_cc.py

## ERROR: BLRUiVXeZKU: YouTube said: Unable to extract video data
#$SCRIPT_DIR/source/youtube/intgr_convert_youtube_dl.py

$SCRIPT_DIR/source/youtube/intgr_convert_yt_dlp_featured.py
$SCRIPT_DIR/source/youtube/intgr_convert_yt_dlp_playlist.py
$SCRIPT_DIR/source/youtube/intgr_convert_yt_dlp_video.py
$SCRIPT_DIR/source/youtube/intgr_convert_yt_dlp_videos.py

$SCRIPT_DIR/source/youtube/intgr_convert_yt1s_com.py

$SCRIPT_DIR/source/youtube/intgr_ytconverter.py

## unfinished
#$SCRIPT_DIR/source/youtube/selenium_example.py


echo -e "\nall tests completed"

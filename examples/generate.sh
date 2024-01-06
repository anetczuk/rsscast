#!/bin/bash

set -eu

## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


SRC_PATH="${SCRIPT_DIR}/../src"
IN_DATA_PATH="${SRC_PATH}/testrsscast/data"

CONVERTER_PATH="${SRC_PATH}/rssconvert.py"


${CONVERTER_PATH} ytrss --infile ${IN_DATA_PATH}/yt_feed_latino_short.xml --outdir ${SCRIPT_DIR}/ytrss/ytlatino

${CONVERTER_PATH} ytrss --infile ${IN_DATA_PATH}/yt_feed_przygody.xml --outdir ${SCRIPT_DIR}/ytrss/przygody

${CONVERTER_PATH} ytdlp --infile ${IN_DATA_PATH}/yt_dlp_playlist_gwiazdowski.json --outdir ${SCRIPT_DIR}/ytdlp/gwiazdowski

${CONVERTER_PATH} ytdlp --infile ${IN_DATA_PATH}/yt_dlp_videos_przygody.json --outdir ${SCRIPT_DIR}/ytdlp/przygody

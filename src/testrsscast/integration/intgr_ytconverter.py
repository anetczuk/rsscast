#!/usr/bin/env python3
##
##
##

try:
    ## following import success only when file is directly executed from command line
    ## otherwise will throw exception when executing as parameter for "python -m"
    # pylint: disable=W0611
    import __init__
except ImportError:
    ## when import fails then it means that the script was executed indirectly
    ## in this case __init__ is already loaded
    pass

import logging

from rsscast.rss.ytconverter import get_yt_duration, convert_yt


_LOGGER = logging.getLogger(__name__)


logging.basicConfig( level=logging.DEBUG )


## =================================================================


def test_01():
    url = 'https://www.youtube.com/watch?v=gNs_9xFisdE'
    duration = get_yt_duration( url )
    if duration != 1152:
        _LOGGER.error( "===== test failed: unable to read video proper length" )
    else:
        length_m = int(duration / 60)
        length_s = int(duration % 60)
        _LOGGER.info( f'length: {duration} = {length_m}m {length_s}s' )

    output_path = "/tmp/test_convert_00.data"
    _LOGGER.info( "converting video: %s into %s", url, output_path )

    status = convert_yt( url, output_path )
    _LOGGER.info( "conversion status: %s", status )
    if not status:
        _LOGGER.error( "===== test failed: unable to convert video" )


def test_02():
    url = "https://www.youtube.com/watch?v=1cpyexbmMyU"
    output_path = "/tmp/test_convert_01.data"
    _LOGGER.info( f"downloading {url}" )
    status = convert_yt( url, output_path )
    _LOGGER.info( "conversion status: %s", status )
    if not status:
        _LOGGER.error( "===== test failed: unable to convert video" )


def test_03():
    url = "https://www.youtube.com/watch?v=ZGMNaHINvuI"
    #url = "https://www.youtube.com/watch?v=2p8OTosmFHU"
    output_path = "/tmp/test_convert_02.data"
    _LOGGER.info( f"downloading {url}" )
    status = convert_yt( url, output_path )
    _LOGGER.info( "conversion status: %s", status )
    if not status:
        _LOGGER.error( "===== test failed: unable to convert video" )


# test_01()

# test_02()

test_03()


_LOGGER.info( "all tests done" )

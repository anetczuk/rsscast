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

from rsscast.rss.ytconverter import get_yt_duration


_LOGGER = logging.getLogger(__name__)


logging.basicConfig( level=logging.DEBUG )


url = 'https://www.youtube.com/watch?v=gNs_9xFisdE'
duration = get_yt_duration( url )

length_m = int(duration / 60)
length_s = int(duration % 60)

print( f'length: {duration} = {length_m}m {length_s}s' )

"""
Handling Ctrl+C inside PyQt.

The code is taken from:
               https://coldfix.eu/2016/11/08/pyqt-boilerplate/

As stated on the website (https://coldfix.eu/about/), content and source code
is published under CC BY and CC0 license respectively.
"""

import signal
import logging
from typing import List, Callable

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication


_LOGGER = logging.getLogger(__name__)


interrupt_handlers: List[ Callable ] = []                 ## list of handlers


def _list_handler(signum, frame):
    _LOGGER.debug("Interrupt received: %s", signum)
    for handler in reversed( interrupt_handlers ):
        handler( signum, frame )


# Define this as a global function to make sure it is not garbage
# collected when going out of scope:
# def _interrupt_handler(signum, frame):
# def _exit_qt_handler( *args ):
def _exit_qt_handler( *_ ):
    """Handle KeyboardInterrupt: quit application."""
    QApplication.exit(2)


def safe_timer(timeout):
    """
    Create a timer that is safe against garbage collection and overlapping calls.

    See: http://ralsina.me/weblog/posts/BB974.html
    """
    def timer_event():
#         try:
#             if func is not None:
#                 func(*args, **kwargs)
#         finally:
#             QtCore.QTimer.singleShot(timeout, timer_event)
        QtCore.QTimer.singleShot(timeout, timer_event)

    QtCore.QTimer.singleShot(timeout, timer_event)


# Call this function in your main after creating the QApplication
def setup_interrupt_handling():
    add_interrupt_handling( _exit_qt_handler )


def add_interrupt_handling( handler ):
    if interrupt_handlers:
        ## not empty
        interrupt_handlers.append( handler )
        return

    ## first call
    interrupt_handlers.append( handler )

    ## Set up handling of KeyboardInterrupt (Ctrl-C) for PyQt.
    signal.signal( signal.SIGINT, _list_handler )

    # Regularly run some (any) python code, so the signal handler gets a
    # chance to be executed:
    safe_timer(100)

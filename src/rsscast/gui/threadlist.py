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

import logging
import threading
import datetime

from multiprocessing import Process

from PyQt5 import QtCore
from PyQt5.QtCore import Qt


_LOGGER = logging.getLogger(__name__)


class ThreadList():

    def __init__(self):
        self.threads = list()

    def append(self, thread: threading.Thread, startThread=False):
        if startThread:
            thread.start()
        self.threads.append( thread )

    def appendStart(self, thread: threading.Thread):
        self.append( thread, True )

    def start(self):
        for thr in self.threads:
            thr.start()

    def join(self):
        for thr in self.threads:
            thr.join()


## ============================================================


class ParallelWorker( QtCore.QObject ):

    finished = QtCore.pyqtSignal()

    def __init__(self, calculationFunctor, parent=None):
        super().__init__( None )

        self.calculationFunctor = calculationFunctor

        self.thread = QtCore.QThread( parent )
        self.moveToThread( self.thread )

        self.thread.started.connect( self._processWorker, Qt.QueuedConnection )
        self.thread.finished.connect( self.finished )
        #### deleted by parent
#         self.thread.finished.connect( self.thread.deleteLater )

#         self.destroyed.connect( ParallelWorker._destroyed )
#         self.thread.destroyed.connect( ParallelWorker._threadDestroyed )
#
#     ## static method is required, because "destroyed" is triggered after
#     ## destruction of Python object (Qt object still exists)
#     @staticmethod
#     def _destroyed(self):
#         _LOGGER.info("worker destroyed")
#
#     ## static method is required, because "destroyed" is triggered after
#     ## destruction of Python object (Qt object still exists)
#     @staticmethod
#     def _threadDestroyed():
#         _LOGGER.info("worker thread destroyed")

    def start(self):
        self.thread.start()

    def wait(self):
        self.thread.wait()

    def _processWorker(self):
        try:
            self.calculationFunctor()
        # pylint: disable=W0703
        except Exception:
            _LOGGER.exception("work terminated" )
        finally:
            self.thread.quit()


## mostly for debugging
class SerialWorker( QtCore.QObject ):

    finished = QtCore.pyqtSignal()

    def __init__(self, calculationFunctor, parent=None):
        super().__init__( parent )

        self.calculationFunctor = calculationFunctor
        ## deleted by parent
#         self.finished.connect( self.deleteLater )

    def start(self):
        self._processWorker()

    def wait(self):
        ## do nothing
        pass

    def _processWorker(self):
        try:
            self.calculationFunctor()
        # pylint: disable=W0703
        except Exception:
            _LOGGER.exception("work terminated" )
        finally:
            self.finished.emit()


## =======================================================================


class WorkerTask():

    def __init__(self, func, args=None):
        if args is None:
            args = []
        self.func   = func
        self.args   = args
        self.result = None

    def __call__(self):
#         _LOGGER.info("executing function: %s %s", self.func, self.args)
        if self.func is not None:
            self.result = self.func( *self.args )
#         _LOGGER.info("executing finished")


class QThreadList( QtCore.QObject ):

    finished = QtCore.pyqtSignal()

    def __init__(self, parent=None, singleThreaded=False ):
        super().__init__( parent )
        self.workers = list()
        self.finishCounter = 0
        self.singleThreaded = singleThreaded

#         self.destroyed.connect( QThreadList._destroyed )
#
#     ## static method is required, because "destroyed" is triggered after
#     ## destruction of Python object (Qt object still exists)
#     @staticmethod
#     def _destroyed():
#         _LOGGER.info("worker list destroyed")

    def deleteOnFinish(self):
        self.finished.connect( self.deleteLater )

    def appendFunction(self, function, args=None):
        task = WorkerTask( function, args )
        worker = None
        if self.singleThreaded:
            worker = SerialWorker( task, self )
        else:
            worker = ParallelWorker( task, self )
        worker.finished.connect( self._workerFinished )
        #### workers will be deleted with parent
#         worker.finished.connect( worker.deleteLater )
        self.workers.append( worker )

#     def map(self, func, argsList):
#         for arg in argsList:
#             self.appendFunction( func, arg )

    def start(self):
        _LOGGER.info( "starting workers" )
        if len(self.workers) < 1:
            ## nothing to do
            self._computingFinished()
            return
        for thr in self.workers:
            thr.start()

    def join(self):
        for thr in self.workers:
            thr.wait()

    def _workerFinished(self):
        self.finishCounter += 1
        ## _LOGGER.info( "thread finished: %d %d", self.finishCounter, len( self.workers ) )
        if self.finishCounter == len( self.workers ):
            self._computingFinished()

    def _computingFinished(self):
        _LOGGER.info( "all workers finished" )
        self.finished.emit()


class QThreadMeasuredList( QThreadList ):

    def __init__(self, parent=None, singleThreaded=False):
        super().__init__( parent, singleThreaded )
        self.startTime = None

    def start(self):
        self.startTime = datetime.datetime.now()
        super().start()

    def _computingFinished(self):
        endTime = datetime.datetime.now()
        diffTime = endTime - self.startTime
        _LOGGER.info( "computation time: %s", diffTime )
        super()._computingFinished()

    @staticmethod
    def calculate( parent, function, args=None ):
        threads = QThreadMeasuredList( parent )
        threads.deleteOnFinish()
        threads.appendFunction( function, args )
        threads.start()


## ====================================================================


class SerialList( QtCore.QObject ):

    finished = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__( parent )
        self.commandsList = list()
        self.startTime = None

    def appendFunction(self, function, args=None):
        self.commandsList.append( (function, args) )

    def start(self):
        self.startTime = datetime.datetime.now()
        _LOGGER.info( "starting computation" )
        for func, args in self.commandsList:
            if func is not None:
                func( *args )
        self.finished.emit()
        endTime = datetime.datetime.now()
        diffTime = endTime - self.startTime
        _LOGGER.info( "computation time: %s", diffTime )

    def join(self):
        pass


## ====================================================================


class ProcessTask():

    def __init__(self, func, args=None):
        if args is None:
            args = []
        self.func = func
        self.args = args

    def __call__(self):
#         _LOGGER.info("executing function: %s %s", self.func, self.args)
        process = Process( target=self.func, args=self.args )
        process.start()
        process.join()
#         _LOGGER.info("executing finished")


class ProcessList( QtCore.QObject ):

    finished = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__( parent )
        self.threads = list()
        self.finishCounter = 0
        self.startTime = None

    def appendFunction(self, function, args=None):
        task = ProcessTask( function, args )
        worker = ParallelWorker( task, self )
        worker.finished.connect( self._threadFinished )
        self.threads.append( worker )

    def start(self):
        _LOGGER.info( "starting processes" )
        self.startTime = datetime.datetime.now()
        for thr in self.threads:
            thr.start()

    def join(self):
        for thr in self.threads:
            thr.wait()

    def _threadFinished(self):
        #_LOGGER.info( "process finished" )
        self.finishCounter += 1
        if self.finishCounter == len( self.threads ):
            self._computingFinished()

    def _computingFinished(self):
        _LOGGER.info( "all processes finished" )
        self.finished.emit()
        endTime = datetime.datetime.now()
        diffTime = endTime - self.startTime
        _LOGGER.info( "computation time: %s", diffTime )

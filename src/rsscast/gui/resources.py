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

from PyQt5 import QtCore
from PyQt5.QtWidgets import qApp


def get_image_path(imageName):
    imgDir = get_images_path()
    path = imgDir + os.path.sep + imageName
    return path


def get_images_path():
    scriptDir = os.path.dirname(os.path.realpath(__file__))
    imgDir = scriptDir + os.path.sep + 'img'
    return imgDir


def get_root_path():
    scriptDir = os.path.dirname( os.path.realpath(__file__) )
    rootDir = scriptDir
    for _ in range(0, 3):
        rootDir = rootDir + os.path.sep + '..'
    rootDir = os.path.abspath( rootDir )
    return rootDir


def get_user_data_path():
    settings = get_settings()
    settingsDir = settings.fileName()
    settingsDir = settingsDir[0:-4]       ## remove extension
    settingsDir += "-data"
    return settingsDir


def get_settings( parent=None ):
    ## store in home directory
    orgName = qApp.organizationName()
    appName = qApp.applicationName()
    settings = QtCore.QSettings(QtCore.QSettings.IniFormat, QtCore.QSettings.UserScope, orgName, appName, parent)
    return settings

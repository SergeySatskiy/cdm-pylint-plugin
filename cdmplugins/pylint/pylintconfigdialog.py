# -*- coding: utf-8 -*-
#
# codimension - graphics python two-way code editor and analyzer
# Copyright (C) 2010-2019  Sergey Satskiy <sergey.satskiy@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""Codimension pylint plugin configuration dialog.

   It is rather an 'about' type dialog at the moment.
"""

import os.path
import pkg_resources
from ui.qt import (QDialog, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy,
                   QPixmap, Qt, QDialogButtonBox)


PLUGIN_HOME_DIR = os.path.dirname(os.path.abspath(__file__)) + os.path.sep


def getPluginVersionAndPath():
    """Provides the plugin version"""
    with open(PLUGIN_HOME_DIR + 'pylint.cdmp') as dec_file:
        for line in dec_file:
            line = line.strip()
            if line.startswith('Version'):
                return line.split('=')[1].strip(), PLUGIN_HOME_DIR
    return 'Unknown', PLUGIN_HOME_DIR


def getPylintVersionAndPath():
    """Provides the pylint version"""
    try:
        return pkg_resources.get_distribution('pylint').version, \
               pkg_resources.get_distribution('pylint').location
    except pkg_resources.DistributionNotFound as exc:
        return 'Unknown', 'Unknown'


class PylintPluginConfigDialog(QDialog):

    """Pyling plugin config dialog"""

    def __init__(self, parent):
        QDialog.__init__(self, parent)

        self.__createLayout()
        self.setWindowTitle('Pylint plugin information')

    def __createLayout(self):
        """Creates the dialog layout"""
        self.resize(320, 120)
        self.setSizeGripEnabled(True)

        pluginVersion, pluginPath = getPluginVersionAndPath()
        pylintVersion, pylintPath = getPylintVersionAndPath()

        vboxLayout = QVBoxLayout(self)
        hboxLayout = QHBoxLayout()
        iconLabel = QLabel()
        iconLabel.setPixmap(QPixmap(PLUGIN_HOME_DIR + 'pylint.png'))
        iconLabel.setScaledContents(True)
        iconLabel.setFixedSize(48, 48)
        hboxLayout.addWidget(iconLabel)
        titleLabel = QLabel('<b>Codimension pylint plugin</b>')
        titleLabel.setSizePolicy(QSizePolicy.Expanding,
                                 QSizePolicy.Expanding)
        titleLabel.setFixedHeight(48)
        titleLabel.setAlignment(Qt.AlignCenter)

        infoLabel = QLabel('<hr><br>More info:'
                           '<ul>'
                           '<li>Plugin<br>'
                           'Version: ' + pluginVersion + '<br>'
                           'Location: ' + pluginPath + '</li>'
                           '<li>Pylint<br>'
                           'Version: ' + pylintVersion + '<br>' +
                           'Location: ' + pylintPath + '</li>'
                           '</ul><br>')
        hboxLayout.addWidget(titleLabel)
        vboxLayout.addLayout(hboxLayout)
        vboxLayout.addWidget(infoLabel)

        self.__buttonBox = QDialogButtonBox(self)
        self.__buttonBox.setOrientation(Qt.Horizontal)
        self.__buttonBox.setStandardButtons(QDialogButtonBox.Ok)
        self.__buttonBox.accepted.connect(self.close)
        self.__buttonBox.rejected.connect(self.close)
        vboxLayout.addWidget(self.__buttonBox)


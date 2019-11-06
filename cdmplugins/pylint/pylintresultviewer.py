# -*- coding: utf-8 -*-
#
# codimension - graphics python two-way code editor and analyzer
# Copyright (C) 2019  Sergey Satskiy <sergey.satskiy@gmail.com>
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

"""Codimension pylint results viewer"""


from ui.qt import (QWidget, QLabel, QPalette, QSizePolicy, QAction, Qt,
                   QHBoxLayout, QToolBar, QSize, QIcon)
from utils.pixmapcache import getIcon
from utils.globals import GlobalData


class PylintResultViewer(QWidget):

    """Pylint results viewer"""

    def __init__(self, pluginHomeDir, parent=None):
        QWidget.__init__(self, parent)

        self.__pluginHomeDir = pluginHomeDir

        self.__noneLabel = QLabel("\nNo results available")
        self.__noneLabel.setAlignment(Qt.AlignHCenter)
        self.__headerFont = self.__noneLabel.font()
        self.__headerFont.setPointSize(self.__headerFont.pointSize() + 4)
        self.__noneLabel.setFont(self.__headerFont)
        self.__noneLabel.setAutoFillBackground(True)
        noneLabelPalette = self.__noneLabel.palette()
        noneLabelPalette.setColor(QPalette.Background,
                                  GlobalData().skin['nolexerPaper'])
        self.__noneLabel.setPalette(noneLabelPalette)

        self.__createLayout(self.__pluginHomeDir, parent)

    def __createLayout(self, pluginHomeDir, parent):
        """Creates the layout"""
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.clearButton = QAction(getIcon('trash.png'), 'Clear', self)
        self.clearButton.triggered.connect(self.__clear)

        self.outputButton = QAction(QIcon(pluginHomeDir + 'output.png'),
                                    'Show output', self)
        self.outputButton.triggered.connect(self.__showOutput)

        self.toolbar = QToolBar(self)
        self.toolbar.setOrientation(Qt.Vertical)
        self.toolbar.setMovable(False)
        self.toolbar.setAllowedAreas(Qt.RightToolBarArea)
        self.toolbar.setIconSize(QSize(16, 16))
        self.toolbar.setFixedWidth(28)
        self.toolbar.setContentsMargins(0, 0, 0, 0)

        self.toolbar.addAction(self.outputButton)
        self.toolbar.addWidget(spacer)
        self.toolbar.addAction(self.clearButton)

        self.__hLayout = QHBoxLayout()
        self.__hLayout.setContentsMargins(0, 0, 0, 0)
        self.__hLayout.setSpacing(0)
        self.__hLayout.addWidget(self.toolbar)
        self.__hLayout.addWidget(self.__noneLabel)
        # self.__hLayout.addWidget(self.__resultsTree)

        self.setLayout(self.__hLayout)


    def __clear(self):
        pass

    def __showOutput(self):
        pass

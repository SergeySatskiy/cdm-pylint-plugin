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


import os.path
from ui.qt import (QWidget, QLabel, QPalette, QSizePolicy, QAction, Qt,
                   QHBoxLayout, QVBoxLayout, QToolBar, QSize, QIcon,
                   QTreeWidget, QTreeWidgetItem, QHeaderView, QFrame)
from ui.itemdelegates import NoOutlineHeightDelegate
from ui.fitlabel import FitPathLabel
from utils.pixmapcache import getIcon
from utils.globals import GlobalData
from utils.colorfont import getLabelStyle
from .pylintoutput import PylintStdoutStderrViewer


class MessageTableItem(QTreeWidgetItem):

    """One message item"""

    def __init__(self, items):
        QTreeWidgetItem.__init__(self, items)

    def __lt__(self, other):
        """Custom comparison"""
        sortColumn = self.treeWidget().sortColumn()
        if sortColumn == 0:
            return int(self.text(sortColumn)) < int(other.text(sortColumn))
        return self.text(sortColumn) < other.text(sortColumn)


class MessageTypeTableItem(QTreeWidgetItem):

    """One message type item"""

    def __init__(self, items):
        QTreeWidgetItem.__init__(self, items)


class PylintResultViewer(QWidget):

    """Pylint results viewer"""

    def __init__(self, ide, pluginHomeDir, parent=None):
        QWidget.__init__(self, parent)

        self.__results = None
        self.__ide = ide
        self.__pluginHomeDir = pluginHomeDir

        self.__noneLabel = QLabel("\nNo results available")
        self.__noneLabel.setFrameShape(QFrame.StyledPanel)
        self.__noneLabel.setAlignment(Qt.AlignHCenter)
        font = self.__noneLabel.font()
        font.setPointSize(font.pointSize() + 4)
        self.__noneLabel.setFont(font)
        self.__noneLabel.setAutoFillBackground(True)
        noneLabelPalette = self.__noneLabel.palette()
        noneLabelPalette.setColor(QPalette.Background,
                                  GlobalData().skin['nolexerPaper'])
        self.__noneLabel.setPalette(noneLabelPalette)

        self.__createLayout(self.__pluginHomeDir)

    def __createLayout(self, pluginHomeDir):
        """Creates the layout"""
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.clearButton = QAction(getIcon('trash.png'), 'Clear', self)
        self.clearButton.triggered.connect(self.clear)

        self.outputButton = QAction(QIcon(pluginHomeDir + 'output.png'),
                                    'Show pylint raw stdout and stderr', self)
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

        self.__resultsTree = QTreeWidget(self)
        self.__resultsTree.setAlternatingRowColors(True)
        self.__resultsTree.setRootIsDecorated(True)
        self.__resultsTree.setItemsExpandable(True)
        self.__resultsTree.setUniformRowHeights(True)
        self.__resultsTree.setItemDelegate(NoOutlineHeightDelegate(4))
        headerLabels = ['Message type / line', 'id', 'Message']
        self.__resultsTree.setHeaderLabels(headerLabels)
        self.__resultsTree.itemActivated.connect(self.__resultActivated)

        self.__fileLabel = FitPathLabel()
        labelStylesheet = 'QLabel {' + getLabelStyle(self.__fileLabel) + '}'
        self.__fileLabel.setStyleSheet(labelStylesheet)
        self.__fileLabel.setAlignment(Qt.AlignLeft)
        self.__fileLabel.setMinimumWidth(50)
        self.__fileLabel.setSizePolicy(QSizePolicy.Expanding,
                                       QSizePolicy.Fixed)
        self.__rateLabel = QLabel()
        self.__rateLabel.setStyleSheet(labelStylesheet)
        self.__rateLabel.setToolTip('pylint analysis rate out of 10 '
                                    '(previous run if there was one)')
        self.__timestampLabel = QLabel()
        self.__timestampLabel.setStyleSheet(labelStylesheet)
        self.__timestampLabel.setToolTip('pylint analysis timestamp')
        self.__labelLayout = QHBoxLayout()
        self.__labelLayout.setSpacing(4)
        self.__labelLayout.addWidget(self.__fileLabel)
        self.__labelLayout.addWidget(self.__rateLabel)
        self.__labelLayout.addWidget(self.__timestampLabel)

        self.__vLayout = QVBoxLayout()
        self.__vLayout.setSpacing(4)
        self.__vLayout.addLayout(self.__labelLayout)
        self.__vLayout.addWidget(self.__resultsTree)

        self.__hLayout = QHBoxLayout()
        self.__hLayout.setContentsMargins(0, 0, 0, 0)
        self.__hLayout.setSpacing(0)
        self.__hLayout.addWidget(self.toolbar)
        self.__hLayout.addWidget(self.__noneLabel)
        self.__hLayout.addLayout(self.__vLayout)

        self.setLayout(self.__hLayout)
        self.__updateButtons()

    def __updateButtons(self):
        """Updates the toolbar buttons approprietly"""
        self.clearButton.setEnabled(self.__results is not None)

        if self.__results is not None:
            stdout = self.__results.get('StdOut', None)
            stderr = self.__results.get('StdErr', None)
            self.outputButton.setEnabled(stdout is not None or
                                         stderr is not None)
        else:
            self.outputButton.setEnabled(False)

    def showResults(self, results):
        """Populates the analysis results"""
        self.clear()
        self.__noneLabel.setVisible(False)
        self.__fileLabel.setVisible(True)
        self.__rateLabel.setVisible(True)
        self.__timestampLabel.setVisible(True)
        self.__resultsTree.setVisible(True)

        self.__results = results
        self.__updateButtons()

        tooltip = ' '.join(['pylint results for',
                            os.path.basename(results['FileName']),
                            'at',
                            results['Timestamp']])
        self.__ide.sideBars['bottom'].setTabToolTip('pylint', tooltip)

        self.__fileLabel.setPath(results['FileName'])
        if 'Rate' in results:
            text = str(results['Rate'])
            if 'PreviousRunRate' in results:
                text += ' (' + str(results['PreviousRunRate']) + ')'
            self.__rateLabel.setText(' ' + text + ' ')
        else:
            self.__rateLabel.setVisible(False)
        self.__timestampLabel.setText(results['Timestamp'])

        totalMessages = 0
        totalMessages += self.__populateMessages('Errors')
        totalMessages += self.__populateMessages('Warnings')
        totalMessages += self.__populateMessages('Refactoring')
        totalMessages += self.__populateMessages('Cosmetics')

        # Update the header with the total number of matches
        headerLabels = ['Message type / line', 'id',
                        'Message (total messages: ' + str(totalMessages) + ')']
        self.__resultsTree.setHeaderLabels(headerLabels)

        # Resizing
        self.__resultsTree.header().resizeSections(
            QHeaderView.ResizeToContents)

    def __populateMessages(self, title):
        """Populates the analysis messages"""
        count = len(self.__results[title[0]])
        if count > 0:
            suffix = '' if count == 1 else 's'
            messageTypeItem = MessageTypeTableItem(
                [title, '', '(' + str(count) + ' message' + suffix + ')'])
            self.__resultsTree.addTopLevelItem(messageTypeItem)
            for item in self.__results[title[0]]:
                columns = [str(item[1]), item[3], item[2]]
                messageItem = MessageTableItem(columns)
                messageTypeItem.addChild(messageItem)
            messageTypeItem.setExpanded(True)
        return count

    def clear(self):
        """Clears the results view"""
        self.__results = None
        self.__updateButtons()

        tooltip = 'No results available'
        self.__ide.sideBars['bottom'].setTabToolTip('pylint', tooltip)
        self.__noneLabel.setVisible(True)

        self.__fileLabel.setVisible(False)
        self.__rateLabel.setVisible(False)
        self.__timestampLabel.setVisible(False)
        self.__resultsTree.setVisible(False)
        self.__resultsTree.clear()

    def __resultActivated(self, item, column):
        """Handles the double click (or Enter) on a message"""
        del column  # unused argument
        if self.__results:
            if isinstance(item, MessageTableItem):
                fileName = self.__results['FileName']
                lineNumber = int(item.data(0, Qt.DisplayRole))
                self.__ide.mainWindow.openFile(fileName, lineNumber)

    def __showOutput(self):
        """Shows the analysis stdout and stderr"""
        if self.__results is None:
            return

        # Show a separate dialog
        PylintStdoutStderrViewer(self.__ide.mainWindow,
                                 self.__results).exec_()


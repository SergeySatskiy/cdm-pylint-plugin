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

"""Codimension pylint plugin implementation"""


import logging
import os.path
from plugins.categories.wizardiface import WizardInterface
from ui.qt import QWidget, QIcon, QTabBar
from ui.mainwindowtabwidgetbase import MainWindowTabWidgetBase
from .pylintdriver import PylintDriver
from .pylintconfigdialog import PylintPluginConfigDialog
from .pylintresultviewer import PylintResultViewer


PLUGIN_HOME_DIR = os.path.dirname(os.path.abspath(__file__)) + os.path.sep


class PylintPlugin(WizardInterface):

    """Codimension pylint plugin"""

    def __init__(self):
        WizardInterface.__init__(self)
        self.__runAction = None
        self.__pylintDriver = None

    @staticmethod
    def isIDEVersionCompatible(ideVersion):
        """Checks if the IDE version is compatible with the plugin.

        Codimension makes this call before activating a plugin.
        The passed ideVersion is a string representing
        the current IDE version.
        True should be returned if the plugin is compatible with the IDE.
        """
        return True

    def activate(self, ideSettings, ideGlobalData):
        """Activates the plugin.

        The plugin may override the method to do specific
        plugin activation handling.

        ideSettings - reference to the IDE Settings singleton
                      see codimension/src/utils/settings.py
        ideGlobalData - reference to the IDE global settings
                        see codimension/src/utils/globals.py

        Note: if overriden do not forget to call the
              base class activate()
        """
        WizardInterface.activate(self, ideSettings, ideGlobalData)

        self.ide.sideBars['bottom'].addTab(PylintResultViewer(PLUGIN_HOME_DIR),
                                           QIcon(PLUGIN_HOME_DIR + 'pylint.png'),
                                           'Pylint', 'pylint', 2)
        self.ide.sideBars['bottom'].tabButton('pylint', QTabBar.RightSide).resize(0, 0)

        self.__pylintDriver = PylintDriver(self.ide)
        self.__pylintDriver.sigFinished.connect(self.__pylintFinished)

    def deactivate(self):
        """Deactivates the plugin.

        The plugin may override the method to do specific
        plugin deactivation handling.
        Note: if overriden do not forget to call the
              base class deactivate()
        """
        self.ide.sideBars['bottom'].removeTab('pylint')

        # self.__runAction.setShortcut('')
        self.__runAction = None
        self.__pylintDriver = None

        WizardInterface.deactivate(self)

    def getConfigFunction(self):
        """Provides a plugun configuration function.

        The plugin can provide a function which will be called when the
        user requests plugin configuring.
        If a plugin does not require any config parameters then None
        should be returned.
        By default no configuring is required.
        """
        return self.configure

    def populateMainMenu(self, parentMenu):
        """Populates the main menu.

        The main menu looks as follows:
        Plugins
            - Plugin manager (fixed item)
            - Separator (fixed item)
            - <Plugin #1 name> (this is the parentMenu passed)
            ...
        If no items were populated by the plugin then there will be no
        <Plugin #N name> menu item shown.
        It is suggested to insert plugin configuration item here if so.
        """
        # parentMenu.addAction("Collect garbage", self.__collectGarbage)

    def populateFileContextMenu(self, parentMenu):
        """Populates the file context menu.

        The file context menu shown in the project viewer window will have
        an item with a plugin name and subitems which are populated here.
        If no items were populated then the plugin menu item will not be
        shown.

        When a callback is called the corresponding menu item will have
        attached data with an absolute path to the item.
        """
        return

    def populateDirectoryContextMenu(self, parentMenu):
        """Populates the directory context menu.

        The directory context menu shown in the project viewer window will
        have an item with a plugin name and subitems which are populated
        here. If no items were populated then the plugin menu item will not
        be shown.

        When a callback is called the corresponding menu item will have
        attached data with an absolute path to the directory.
        """
        return

    def populateBufferContextMenu(self, parentMenu):
        """Populates the editing buffer context menu.

        The buffer context menu shown for the current edited/viewed file
        will have an item with a plugin name and subitems which are
        populated here. If no items were populated then the plugin menu
        item will not be shown.

        Note: when a buffer context menu is selected by the user it always
              refers to the current widget. To get access to the current
              editing widget the plugin can use: self.ide.currentEditorWidget
              The widget could be of different types and some circumstances
              should be considered, e.g.:
              - it could be a new file which has not been saved yet
              - it could be modified
              - it could be that the disk file has already been deleted
              - etc.
              Having the current widget reference the plugin is able to
              retrieve the information it needs.
        """
        self.__runAction = parentMenu.addAction(
            QIcon(PLUGIN_HOME_DIR + 'pylint.png'), 'Run pylint', self.__run,
            'Ctrl+L')
        self.__runAction.setShortcut('Ctrl+L')

    def configure(self):
        """Configure dialog"""
        PylintPluginConfigDialog(self.ide.mainWindow).exec_()

    def __run(self):
        """Runs the pylint analysis"""
        editorWidget = self.ide.currentEditorWidget
        if editorWidget.getType() == MainWindowTabWidgetBase.PlainTextEditor:
            print(editorWidget)
            print('Asked to run pylint')
            self.__pylintDriver.start(editorWidget.getFileName(), None)

    def __pylintFinished(self, results):
        """Pylint has finished"""
        error = results.get('ProcessError', None)
        if error:
            logging.error(error)
            return

        print(results)

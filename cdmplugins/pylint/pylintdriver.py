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

"""Codimension pylint driver implementation"""


import sys
import re
import os.path
from ui.qt import QWidget, pyqtSignal, QProcess, QProcessEnvironment, QByteArray
from utils.misc import getLocaleDateTime

MSG_REGEXP = re.compile(r'^[CRWE]+([0-9]{4})?:')


class PylintDriver(QWidget):

    """Pylint driver which runs pylint in the background"""

    sigFinished = pyqtSignal(dict)

    def __init__(self, ide):
        QWidget.__init__(self)

        self.__ide = ide
        self.__process = None

        self.__stdout = ''
        self.__stderr = ''

    def isInProcess(self):
        """True if pylint is still running"""
        return self.__process is not None

    def start(self, fileName, encoding):
        """Runs the analysis process"""
        if self.__process is not None:
            return 'Another pylint analysis is in progress'

        self.__fileName = fileName
        self.__encoding = 'utf-8' if encoding is None else encoding

        self.__process = QProcess(self)
        self.__process.setProcessChannelMode(QProcess.SeparateChannels)
        self.__process.setWorkingDirectory(os.path.dirname(self.__fileName))
        self.__process.readyReadStandardOutput.connect(self.__readStdOutput)
        self.__process.readyReadStandardError.connect(self.__readStdError)
        self.__process.finished.connect(self.__finished)

        self.__stdout = ''
        self.__stderr = ''

        args = ['-m', 'pylint', '--output-format=text',
                "--msg-template='{msg_id}:{line:3d},{column}: {obj}: {msg}'",
                os.path.basename(self.__fileName)]
        processEnvironment = QProcessEnvironment()
        processEnvironment.insert('PYTHONIOENCODING', self.__encoding)
        self.__process.setProcessEnvironment(processEnvironment)
        self.__process.start(sys.executable, args)

        running = self.__process.waitForStarted()
        if not running:
            self.__process = None
            return 'pylint analysis failed to start'
        return None

    def stop(self):
        """Interrupts the analysis"""
        if self.__process is not None:
            if self.__process.state() == QProcess.Running:
                self.__process.kill()
                self.__process.waitForFinished()
            self.__process = None

    def __readStdOutput(self):
        """Handles reading from stdout"""
        self.__process.setReadChannel(QProcess.StandardOutput)
        qba = QByteArray()
        while self.__process.bytesAvailable():
            qba += self.__process.readAllStandardOutput()
        self.__stdout += str(qba.data(), self.__encoding)

    def __readStdError(self):
        """Handles reading from stderr"""
        self.__process.setReadChannel(QProcess.StandardError)
        qba = QByteArray()
        while self.__process.bytesAvailable():
            qba += self.process.readAllStandardError()
        self.__stderr += str(qba.data(), self.__encoding)

    def __finished(self, exitCode, exitStatus):
        """Handles the process finish"""
        self.__process = None

        if not self.__stdout:
            if self.__stderr:
                self.sigFinished.emit({'ProcessError':
                                       'pylint error:\n' + self.__stderr,
                                       'ExitCode': exitCode,
                                       'ExitStatus': exitStatus,
                                       'FileName': self.__fileName,
                                       'Timestamp': getLocaleDateTime()})
            return

        # Convention, Refactor, Warning, Error
        results = {'C': [], 'R': [], 'W': [], 'E': [],
                   'ExitCode': exitCode,
                   'ExitStatus': exitStatus,
                   'StdOut': self.__stdout,
                   'StdErr': self.__stderr,
                   'FileName': self.__fileName,
                   'Timestamp': getLocaleDateTime()}
        modulePattern = '************* Module '

        module = ''
        for line in self.__stdout.splitlines():
            if line.startswith(modulePattern):
                module = line[len(modulePattern):]
                continue
            if not re.match(r'^[CRWE]+([0-9]{4})?:', line):
                continue
            colonPos1 = line.find(':')
            if colonPos1 == -1:
                continue
            msgId = line[:colonPos1]
            colonPos2 = line.find(':', colonPos1 + 1)
            if colonPos2 == -1:
                continue
            lineNo = line[colonPos1 + 1:colonPos2].strip()
            if not lineNo:
                continue
            lineNo = int(lineNo.split(',')[0])
            message = line[colonPos2 + 1:]
            item = (module, lineNo, message, msgId)
            results[line[0]].append(item)

        # Rate and previous run
        ratePattern = 'Your code has been rated at '
        ratePos = self.__stdout.find(ratePattern)
        if ratePos > 0:
            rateEndPos = self.__stdout.find('/10', ratePos)
            if rateEndPos > 0:
                rate = self.__stdout[ratePos + len(ratePattern):rateEndPos]
                results['Rate'] = rate

                # Previous run
                prevRunPattern = 'previous run: '
                prevRunPos = self.__stdout.find(prevRunPattern, rateEndPos)
                if prevRunPos > 0:
                    prevRunEndPos = self.__stdout.find('/10', prevRunPos)
                    previous = self.__stdout[prevRunPos + len(prevRunPattern):prevRunEndPos]
                    results['PreviousRunRate'] = previous

        self.sigFinished.emit(results)


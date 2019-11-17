# -*- coding: utf-8 -*-
#
# cdmpylintplugin - Codimension IDE pylint plugin
# Copyright (C) 2017  Sergey Satskiy <sergey.satskiy@gmail.com>
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

"""Setup script for the Codimension IDE pylint plugin"""

import sys
import os.path
from setuptools import setup

description = 'Codimension IDE pylint plugin'

plugin_desc_file = 'pylint.cdmp'

def getPluginVersion():
    """The version must be updated in the .cdmp file"""
    desc_file = os.path.join('cdmplugins', 'pylint', plugin_desc_file)
    if not os.path.exists(desc_file):
        print('Cannot find the plugin description file. Expected here: ' +
              desc_file, file=sys.stderr)
        sys.exit(1)

    with open(desc_file) as dec_file:
        for line in dec_file:
            line = line.strip()
            if line.startswith('Version'):
                return line.split('=')[1].strip()
    print('Cannot find a version line in the ' + desc_file,
          file=sys.stderr)
    sys.exit(1)


try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except Exception as exc:
    print('pypandoc package is not installed: the markdown '
          'README.md convertion to rst failed\n' + str(exc), file=sys.stderr)
    import io
    # pandoc is not installed, fallback to using raw contents
    with io.open('README.md', encoding='utf-8') as f:
        long_description = f.read()


setup(name='cdmpylintplugin',
      description=description,
      long_description=long_description,
      version=getPluginVersion(),
      author='Sergey Satskiy',
      author_email='sergey.satskiy@gmail.com',
      url='https://github.com/SergeySatskiy/cdm-pylint-plugin',
      license='GPLv3',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 3'],
      platforms=['any'],
      packages=['cdmplugins', 'cdmplugins.pylint'],
      install_requires=['pylint==2.4.3'],
      package_data={'cdmplugins.pylint': [plugin_desc_file,
                                          'generate.png', 'output.png',
                                          'pylint.png']})

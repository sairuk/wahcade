# -*- coding: utf-8 -*-
#
###
# Application: wah!cade
# File:        setup.py
# Description: setup file
# Copyright (c) 2005-2010   Andy Balcombe <http://www.anti-particle.com>
###
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
from distutils.core import setup
import py2exe
import glob

from constants import *

#don't include any of the gtk runtime dll's
py2exe_opts = {
    "py2exe": {
        "includes": "pango,atk,gobject,cairo,pangocairo",
        "dll_excludes": [
            "iconv.dll",
            "intl.dll",
            "libatk-1.0-0.dll",
            "libgdk_pixbuf-2.0-0.dll",
            "libgdk-win32-2.0-0.dll",
            "libglib-2.0-0.dll",
            "libgmodule-2.0-0.dll",
            "libgobject-2.0-0.dll",
            "libgthread-2.0-0.dll",
            "libgtk-win32-2.0-0.dll",
            "libpango-1.0-0.dll",
            "libpangowin32-1.0-0.dll",
            "libglade-2.0-0.dll",
            "libcairo-2.dll",
            "libfontconfig-1.dll",
            "libfreetype-6.dll",
            "libpng12.dll",
            "libpangocairo-1.0-0.dll",
            "libpangoft2-1.0-0.dll"],
        }
    }

#distutils stuff
setup(
    name = 'Wah!Cade',
    description = 'Wah!Cade - A nice, keyboard controlled frontend for arcade emulators',
    version = VERSION,
    author = 'Andy Balcombe',
    author_email = 'wahcade@anti-particle.com',
    url = 'http://www.anti-particle.com/wahcade',
    #scripts = ['wahcade.py', 'wahcade-setup.py', 'wahcade-layout-editor.py'],
    windows = [
        ({'script': 'wahcade.py', 'icon_resources': [(1, "pixmaps/wahcade.ico")]}),
        ({'script': 'wahcade-setup.py', 'icon_resources': [(1, "pixmaps/wahcade.ico")]}),
        ({'script': 'wahcade-layout-editor.py', 'icon_resources': [(1, "pixmaps/wahcade.ico")]})
    ],
    options = py2exe_opts,
    data_files = [
        ("config.dist", glob.glob("config.dist/*.*")),
        ("config.dist/ctrlr", glob.glob("config.dist/ctrlr/*.*")),
        ("config.dist/files", glob.glob("config.dist/files/*.*")),
        ("config.dist/ini", glob.glob("config.dist/ini/*.*")),
        ("config.dist/layouts", glob.glob("config.dist/layouts/*.*")),
        ("config.dist/layouts/classic_640x480", glob.glob("config.dist/layouts/classic_640x480/*.*")),
        ("config.dist/layouts/classic_800x600", glob.glob("config.dist/layouts/classic_800x600/*.*")),
        ("config.dist/layouts/classic_1024x768", glob.glob("config.dist/layouts/classic_1024x768/*.*")),
        ("config.dist/layouts/cpviewer", glob.glob("config.dist/layouts/cpviewer/*.*")),
        ("doc", glob.glob("doc/[A-Z]*")),
        ("doc/samples", glob.glob("doc/samples/*")),
        ("doc/xmame", glob.glob("doc/xmame/*")),
        ("doc/file_formats", glob.glob("doc/file_formats/*")),
        ("glade", glob.glob("glade/*.*")),
        ("pixmaps", glob.glob("pixmaps/*.png")),
        ("pixmaps", glob.glob("pixmaps/*.ico")),
        ("templates", glob.glob("templates/*.ini"))
    ],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: X11 Applications :: GTK',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows :: Windows NT/2000',
        'Operating System :: POSIX :: BSD :: FreeBSD',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Games/Entertainment :: Arcade'
    ]
)


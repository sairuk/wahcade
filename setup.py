# -*- coding: utf-8 -*-
#
###
# Application: wah!cade
# File:        setup.py
# Description: setup file (for building debian package)
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
import bdist_debian
from distutils.core import setup
import glob

from constants import *


#distutils stuff
setup(
    name = 'wahcade',
    description = "Wah!Cade - A nice, keyboard controlled frontend for arcade emulators.",
    long_description="It's a front end for the M.A.M.E. arcade game emulator, and has been designed with arcade cabinet controls & projects in mind.",
    version = VERSION,
    author = 'Andy Balcombe',
    author_email = 'wahcade@anti-particle.com',
    maintainer = 'Andy Balcombe',
    maintainer_email = 'wahcade@anti-particle.com',
    depends = 'python (>=2.4.0), python-gtk2 (>=2.12.0), python-glade2, python-chardet (>=1.0), python-gst0.10, python-pygame (>=1.6), python-imaging (>=1.1.5)',
    recommends = 'sdlmame',
    section = 'games',
    #suggests = 'python-pygame (>=1.6), python-imaging (>=1.1.5)',
    priority = 'optional',
    url = 'http://www.anti-particle.com/wahcade',
    scripts = ['wahcade', 'wahcade-setup', 'wahcade-layout-editor'],
    data_files = [
        ("share/games/wahcade", glob.glob("*.py")),
        ("share/games/wahcade/config.dist", glob.glob("config.dist/*.*")),
        ("share/games/wahcade/config.dist/ctrlr", glob.glob("config.dist/ctrlr/*.*")),
        ("share/games/wahcade/config.dist/files", glob.glob("config.dist/files/*.*")),
        ("share/games/wahcade/config.dist/ini", glob.glob("config.dist/ini/*.ini")),
        ("share/games/wahcade/config.dist/layouts", glob.glob("config.dist/layouts/*.*")),
        ("share/games/wahcade/config.dist/layouts/classic_480x640", glob.glob("config.dist/layouts/classic_480x640/*.*")),
        ("share/games/wahcade/config.dist/layouts/classic_640x480", glob.glob("config.dist/layouts/classic_640x480/*.*")),
        ("share/games/wahcade/config.dist/layouts/classic_800x600", glob.glob("config.dist/layouts/classic_800x600/*.*")),
        ("share/games/wahcade/config.dist/layouts/classic_1024x768", glob.glob("config.dist/layouts/classic_1024x768/*.*")),
        ("share/games/wahcade/config.dist/layouts/classic_cpviewer", glob.glob("config.dist/layouts/classic_cpviewer/*.*")),
        ("share/games/wahcade/config.dist/layouts/classic_histview", glob.glob("config.dist/layouts/classic_histview/*.*")),
        ("share/games/wahcade/config.dist/layouts/retro_black_640x480", glob.glob("config.dist/layouts/retro_black_640x480/*.*")),
        ("share/games/wahcade/config.dist/layouts/retro_black_800x600", glob.glob("config.dist/layouts/retro_black_800x600/*.*")),
        ("share/games/wahcade/config.dist/layouts/retro_black_1024x768", glob.glob("config.dist/layouts/retro_black_1024x768/*.*")),
        ("share/games/wahcade/config.dist/layouts/retro_white_640x480", glob.glob("config.dist/layouts/retro_white_640x480/*.*")),
        ("share/games/wahcade/config.dist/layouts/retro_white_800x600", glob.glob("config.dist/layouts/retro_white_800x600/*.*")),
        ("share/games/wahcade/config.dist/layouts/retro_white_1024x768", glob.glob("config.dist/layouts/retro_white_1024x768/*.*")),
        ("share/games/wahcade/config.dist/layouts/retro_cpviewer", glob.glob("config.dist/layouts/retro_cpviewer/*.*")),
        ("share/games/wahcade/config.dist/layouts/retro_histview", glob.glob("config.dist/layouts/retro_histview/*.*")),
        ("share/games/wahcade/config.dist/layouts/simple_640x480", glob.glob("config.dist/layouts/simple_640x480/*.*")),
        ("share/games/wahcade/config.dist/layouts/simple_800x600", glob.glob("config.dist/layouts/simple_800x600/*.*")),
        ("share/games/wahcade/config.dist/layouts/simple_1024x768", glob.glob("config.dist/layouts/simple_1024x768/*.*")),
        ("share/games/wahcade/doc", glob.glob("doc/[A-Z]*")),
        ("share/games/wahcade/doc/samples", glob.glob("doc/samples/*")),
        ("share/games/wahcade/doc/xmame", glob.glob("doc/xmame/*")),
        ("share/games/wahcade/doc/file_formats", glob.glob("doc/file_formats/*.txt")),
        ("share/games/wahcade/glade", glob.glob("glade/*.*")),
        ("share/games/wahcade/pixmaps", glob.glob("pixmaps/*.png")),
        ("share/games/wahcade/pixmaps", glob.glob("pixmaps/*.ico")),
        ("share/games/wahcade/templates", glob.glob("templates/*.ini")),
        ("share/applications", glob.glob("*.desktop")),
        ("share/pixmaps", ["pixmaps/wahcade.png", "pixmaps/wahcade-setup.png", "pixmaps/wahcade-layout-editor.png"]),
        ("share/locale/de/LC_MESSAGES", glob.glob("locale/de/LC_MESSAGES/*.mo")),
        ("share/locale/en/LC_MESSAGES", glob.glob("locale/en/LC_MESSAGES/*.mo")),
        ("share/locale/en_GB/LC_MESSAGES", glob.glob("locale/en_GB/LC_MESSAGES/*.mo")),
        ("share/locale/es/LC_MESSAGES", glob.glob("locale/es/LC_MESSAGES/*.mo")),
        ("share/locale/fr/LC_MESSAGES", glob.glob("locale/fr/LC_MESSAGES/*.mo")),
        ("share/locale/sv/LC_MESSAGES", glob.glob("locale/sv/LC_MESSAGES/*.mo")),
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
    ],
    cmdclass={'bdist_debian': bdist_debian.bdist_debian}
)

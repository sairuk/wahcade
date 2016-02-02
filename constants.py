# -*- coding: utf-8 -*-
#
###
# Application: wah!cade
# File:        constants.py
# Description: constants file
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
import os
import locale
import gettext

"""constants"""
#application constants
APP_NAME = 'wahcade'
APP_PATH = os.path.abspath(os.getcwd())
VERSION = 'bzr-devel'
VERSION_NAME = "mahcade"
LAYOUT_GLADE_FILE = os.path.join(APP_PATH, 'glade', 'layout_editor.glade')
SETUP_GLADE_FILE = os.path.join(APP_PATH, 'glade', 'wahcade_setup.glade')
LOCALE_DIR = os.path.join(APP_PATH, 'locale')

if os.path.exists(os.path.join(APP_PATH,'portable.mode')):
    CONFIG_DIR = os.path.expanduser(os.path.join(APP_PATH,'.wahcade'))
else:
    CONFIG_DIR = os.path.expanduser('~/.wahcade')

#locale stuff
try:
    locale.setlocale(locale.LC_ALL, '')
    gettext.bindtextdomain(APP_NAME, LOCALE_DIR)
    gettext.bind_textdomain_codeset(APP_NAME, 'UTF-8')
    gettext.textdomain(APP_NAME)
except locale.Error:
    print 'Warning: Unsupported locale: Defaulting to English'

#mame/mess ini file names
MAME_INI_FILES = ['mame', 'xmame', 'sdlmame', 'advmame', 'mame32', 'mameosx', 'mess', 'xmess', 'sdlmess', 'advmess']

#file types
IMAGE_FILETYPES= ['jpg', 'jpeg', 'png', 'bmp', 'gif','svg']
MOVIE_FILETYPES= ['avi', 'mpg', 'mpeg', 'ogg', 'ogv', 'mp4', 'mov', 'wmv', 'flv', 'mkv']
MUSIC_FILESPEC_NEW = ['mp3', 'ogg', 'oga', 'flac', 'mid']
MUSIC_FILESPEC = '*.ogg;*.oga;*.mp3;*.flac;*.mid'

#maximum number of lists per emulator
MAX_LISTS = 100

#wahcade game list columns
GL_GAME_NAME = 0
GL_ROM_NAME = 1
GL_YEAR = 2
GL_MANUFACTURER = 3
GL_CLONE_OF = 4
GL_ROM_OF = 5
GL_DISPLAY_TYPE = 6
GL_SCREEN_TYPE = 7
GL_CONTROLLER_TYPE = 8
GL_DRIVER_STATUS = 9
GL_COLOUR_STATUS = 10
GL_SOUND_STATUS = 11
GL_CATEGORY = 12

FAV_ROM_NAME = 0
FAV_GAME_NAME = 1
FAV_TIMES_PLAYED = 2
FAV_MINS_PLAYED = 3

FTR_CLONES_NO = 0
FTR_CLONES_YES = 1
FTR_CLONES_BETTER = 2

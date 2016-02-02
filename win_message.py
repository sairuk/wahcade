#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
###
# Application: wah!cade
# File:        win_message.py
# Description: message window
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
import sys
import string
import re

#gtk
import pygtk
if sys.platform != 'win32':
    pygtk.require('2.0')
import gtk
import gobject
import pango

#project modules
from constants import *
from wc_common import WahCade
_ = gettext.gettext


class WinMessage(WahCade):
    """Wah!Cade Message Window"""

    def __init__(self, WinMain):
        #set main window
        self.WinMain = WinMain
        #build the window
        self.winMessage = gtk.Fixed()
        self.winMessage.set_has_window(True)
        self.imgBackground = gtk.Image()
        self.lblHeading = gtk.Label()
        self.lblMessage = gtk.Label()
        self.lblPrompt = gtk.Label()
        self.lblHeading.set_justify(gtk.JUSTIFY_CENTER)
        self.lblMessage.set_justify(gtk.JUSTIFY_CENTER)
        self.lblPrompt.set_justify(gtk.JUSTIFY_CENTER)
        self.winMessage.add(self.imgBackground)
        self.winMessage.add(self.lblHeading)
        self.winMessage.add(self.lblMessage)
        self.winMessage.add(self.lblPrompt)
        WinMain.fixd.add(self.winMessage)
        self.imgBackground.show()
        self.lblHeading.show()
        self.lblMessage.show()
        self.lblPrompt.show()
        self.winMessage.show()
        #
        self.wait_for_key = False

    def display_message(self, heading='', message='', prompt='', wait_for_key=False):
        """show the required message"""
        #print "display_message:\n  heading=",heading, "\n  message=",message
        self.lblHeading.set_text(heading)
        self.lblMessage.set_text(message)
        self.lblPrompt.set_text(prompt)
        self.do_events()
        self.WinMain.show_window('message')
        self.do_events()
        self.wait_for_key = wait_for_key

    def hide(self):
        """hide message window"""
        self.wait_for_key = False
        self.WinMain.hide_window('message')
        self.do_events()

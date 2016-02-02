#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
###
# Application: wah!cade
# File:        exception.py
# Description: exception handler
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
import sys
import traceback
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
import pygtk
if sys.platform != 'win32':
    #not win32, ensure version 2 of pygtk is imported
    pygtk.require('2.0')
import gtk
import pango
from gettext import gettext as _


def _info(type, value, tb):
    """display exception"""
    #ungrab a potentially "grabbed" mouse pointer
    gtk.gdk.pointer_ungrab()
    #create dialog
    dialog = gtk.MessageDialog(
        parent = None,
        flags = 0,
        type = gtk.MESSAGE_WARNING,
        buttons = gtk.BUTTONS_NONE,
        message_format = _("<big><b>Error</b></big>"))
    dialog.set_title(_("Bug Detected"))
    dialog.vbox.get_children()[0].get_children()[1].get_children()[0].set_property("use-markup", True)
    dialog.add_button(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)
    #details
    textview = gtk.TextView() 
    textview.show()
    textview.set_editable(False)
    textview.modify_font(pango.FontDescription("Monospace"))
    sw = gtk.ScrolledWindow() 
    sw.show()
    sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    sw.add(textview)
    frame = gtk.Frame()
    frame.set_shadow_type(gtk.SHADOW_IN)
    frame.add(sw)
    frame.set_border_width(6)
    dialog.vbox.add(frame)
    textbuffer = textview.get_buffer()
    trace = StringIO.StringIO()
    traceback.print_exception(type, value, tb, None, trace)
    textbuffer.set_text(trace.getvalue())
    textview.set_size_request(gtk.gdk.screen_width()/2, gtk.gdk.screen_height()/3)
    dialog.details = frame
    dialog.set_position(gtk.WIN_POS_CENTER)
    dialog.set_gravity(gtk.gdk.GRAVITY_CENTER)
    dialog.details.show()
    #display the dialog
    resp = dialog.run()
    if resp == gtk.RESPONSE_CLOSE:
        pass
    dialog.destroy()
    sys.exit(1)

#sys.excepthook = _info


#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
###
# Application: wah!cade
# File:        layout_scr_props.py
# Description: Wah!Cade Layout Screen Properties Dialog
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
from constants import *
from glade2 import *


class DlgScreenProps(GladeSupport):
    """Screen Properties Dialog"""

    def __init__(self, glade_filename, window_name, app):
        """build the window"""
        GladeSupport.__init__(self, glade_filename, window_name)
        #
        self.WinLayout = app
        self.screen_props = None
        self.screen_widget = None
        self.updating = False
        #set open file / dir button images
        btns = [self.btnBackgroundImage] #, self.btnDataFile]
        pb = self.dlgScreenProps.render_icon(gtk.STOCK_OPEN, gtk.ICON_SIZE_MENU)
        for btn in btns:
            img = gtk.Image()
            img.set_from_pixbuf(pb)
            btn.set_image(img)

    def on_dlgScreenProps_delete_event(self, *args):
        self.dlgScreenProps.hide()
        return True

    def on_btnClose_clicked(self, *args):
        """hide screen properties dialog"""
        self.dlgScreenProps.hide()

    def on_cbeWidth_changed(self, *args):
        """change widget width"""
        if not self.updating:
            try:
                w = int(self.cbeWidth.child.get_text())
            except ValueError:
                w = 0
            self.screen_props['width'] = w
            self.screen_widget.set_size_request(w, self.screen_props['height'])
            self.WinLayout.set_layout_altered(self.screen_widget)

    def on_cbeHeight_changed(self, *args):
        """change widget height"""
        if not self.updating:
            try:
                h = int(self.cbeHeight.child.get_text())
            except ValueError:
                h = 0
            self.screen_props['height'] = h
            self.screen_widget.set_size_request(self.screen_props['width'], h)
            self.WinLayout.set_layout_altered(self.screen_widget)

    def on_txeBackgroundImage_changed(self, *args):
        """change window image filename"""
        if not self.updating:
            self.screen_props['image'] = self.txeBackgroundImage.get_text()
            fname = self.WinLayout.get_path(self.txeBackgroundImage.get_text())
            if os.path.isfile(fname):
                #update image
                self.WinLayout.imgBg.set_from_file(fname)
            self.WinLayout.set_layout_altered(self.screen_widget)

    def on_btnBackgroundImage_clicked(self, *args):
        """open background image"""
        dlg = gtk.FileChooserDialog(
            title = 'Pick a background image',
            action = gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        ftr = gtk.FileFilter()
        ftr.set_name("All files")
        ftr.add_pattern("*")
        dlg.add_filter(ftr)
        fname = self.WinLayout.get_path(self.txeBackgroundImage.get_text())
        if os.path.exists(fname):
            dlg.set_filename(fname)
        else:
            dlg.set_current_folder(os.path.dirname(self.WinLayout.layout_filename))
        response = dlg.run()
        if response == gtk.RESPONSE_OK:
            self.chkBackgroundImage.set_active(True)
            self.txeBackgroundImage.set_text(dlg.get_filename())
        dlg.destroy()

    def on_chkBackgroundImage_toggled(self, *args):
        """change window image filename"""
        if not self.updating:
            if not self.chkBackgroundImage.get_active():
                #don't use image
                self.WinLayout.imgBg.set_property('visible', False)
                self.screen_props['use_image'] = False
            else:
                self.WinLayout.imgBg.set_property('visible', True)
                self.screen_props['use_image'] = True
            self.WinLayout.set_layout_altered(self.screen_widget)

    def on_colourBg_color_set(self, widget, *args):
        if not self.updating:
            clr, hex_clr = self.WinLayout.get_colorbutton_info(widget)
            self.screen_props['background-col'] = hex_clr
            self.WinLayout.viewport.modify_bg(gtk.STATE_NORMAL, clr)
            self.WinLayout.set_layout_altered(self.screen_widget)
            #set all transparent childrens background colour too
            for widget in self.WinLayout.fixd.get_children():
                if self.WinLayout.dLayout[widget]['transparent']:
                    widget.modify_bg(gtk.STATE_NORMAL, clr)

    def set_properties(self):
        """set props for current screen"""
        self.updating = True
        self.screen_props = self.WinLayout.dLayout[self.WinLayout.fixd]
        self.screen_widget = self.WinLayout.fixd
        self.txeScreen.set_text(self.screen_props['name'])
        self.cbeWidth.child.set_text(str(self.screen_props['width']))
        self.cbeHeight.child.set_text(str(self.screen_props['height']))
        self.colourBg.set_color(
            gtk.gdk.color_parse(self.screen_props['background-col']))
        #window type
        if self.screen_props != self.WinLayout.dLayout[self.WinLayout.fixdScr]:
            #normal windows
            self.chkBackgroundImage.set_sensitive(True)
            self.txeBackgroundImage.set_sensitive(True)
            self.btnBackgroundImage.set_sensitive(True)
            self.chkBackgroundImage.set_active(self.screen_props['use_image'])
                #os.path.exists(self.WinLayout.get_path(self.screen_props['image'])))
            self.txeBackgroundImage.set_text(self.screen_props['image'])
        else:
            #screen saver window
            self.chkBackgroundImage.set_sensitive(False)
            self.txeBackgroundImage.set_sensitive(False)
            self.btnBackgroundImage.set_sensitive(False)
        self.updating = False

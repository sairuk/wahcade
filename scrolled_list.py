# -*- coding: utf-8 -*-
#
###
# Application: wah!cade
# File:        scrolled_list.py
# Description: Transparent Scrolled List Widget
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
import sys

#gtk
import pygtk
if sys.platform != 'win32':
    pygtk.require('2.0')
import gtk
import gobject
gobject.threads_init()
import pango

class ScrollList:
    """custom scroll list control"""

    def __init__(self):
        """create custom scroll list control"""
        #properties
        self.ls = []
        self.width, self.height = 100, 200
        self.angle = 0
        self.auto_update = False
        self.display_limiters = False
        self.use_mouse = False
        self.wrap_list = False
        self.num_rows = 10
        #internal properties
        self._hl_on_row = 0
        self._ls_idx = 0
        self._ls_idx_old = -1
        self._pango_font_desc = pango.FontDescription('sans 10')
        self._row_height = self.height / self.num_rows
        self._rows = []
        #properties dict
        self.properties = {
            'xalign': 0.5}
        #signals dict
        self.signals = {
            'update': None,
            'mouse-left-click': None,
            'mouse-right-click': None,
            'mouse-double-click': None}
        #default colours
        self._hl_bg_col = gtk.gdk.color_parse('white')
        self._hl_fg_col = gtk.gdk.color_parse('green')
        self._fg_col = gtk.gdk.color_parse('yellow')
        #create the list
        self._create_container()
        self.set_size_request(self.width, self.height)

    def __setattr__(self, var_name, var_value):
        """capture setting of attributes in order to reset _ls_idx_old"""
        self.__dict__[var_name] = var_value
        if self.__dict__[var_name] == self.ls:
            self._ls_idx_old = -1

    def connect(self, signal_name, callback, *args):
        """connect callback functions to signals"""
        if signal_name in self.signals:
            self.signals[signal_name] = callback
        else:
            raise #TypeError, 'unknown signal name'

    def scroll(self, scroll_by):
        """scroll list by given number of rows"""
        self.set_selected(self._ls_idx + scroll_by)

    def update(self):
        """has scroll list position changed"""
        if self._ls_idx != self._ls_idx_old:
            #list pos changed
            self._ls_idx_old = self._ls_idx
            #call update callback function
            if self.signals['update']:
                self.signals['update'](self._ls_idx)
            return True
        else:
            #list pos not changed
            return False

    def get_data(self, k):
        """call gobject get_data"""
        return self.fixd.get_data(k)

    def set_data(self, k, v):
        """call gobject set_data"""
        self.fixd.set_data(k, v)

    def get_selected(self):
        """return index of currently selected item"""
        return self._ls_idx

    def modify_font(self, pango_font_desc):
        """set list font"""
        #save font desc
        self._pango_font_desc = pango_font_desc
        #call resize, which will force rows to be recalculated & displayed
        self.set_size_request(self.width, self.height)

    def modify_highlight_bg(self, gtk_state, hl_bg_col):
        """set list highlighted bar colour"""
        self._hl_bg_col = hl_bg_col
        self.arwScrollTop.modify_bg(gtk_state, self._hl_bg_col)
        self.arwScrollBottom.modify_bg(gtk_state, self._hl_bg_col)
        for i in range(self.num_rows):
            self._rows[i][0].modify_bg(gtk_state, self._hl_bg_col)

    def modify_highlight_fg(self, gtk_state, hl_fg_col):
        """set list highlighted text colour"""
        self._hl_fg_col = hl_fg_col

    def modify_fg(self, gtk_state, fg_col):
        """set list foreground colour"""
        self._fg_col = fg_col
        self.arwScrollTop.modify_fg(gtk_state, self._fg_col)
        self.arwScrollBottom.modify_fg(gtk_state, self._fg_col)
        for i in range(self.num_rows):
            self._rows[i][1].modify_fg(gtk_state, self._fg_col)

    def get_parent(self):
        """return the parent of the scrolled list"""
        return self.fixd.get_parent()

    def set_property(self, property_name, property_value):
        """set property"""
        if property_name in self.properties:
            self.properties[property_name] = property_value
        if property_name.lower() == 'xalign':
            #alignment
            for i in range(self.num_rows):
                self._rows[i][1].set_property('xalign', property_value)

    def set_angle(self, angle):
        """set rotation angle"""
        self.angle = angle

    def set_size_request(self, width, height):
        """change size"""
        self.width, self.height = width, height
        #set list container size
        self.fixd.set_size_request(width, height)
        #angle
        if self.angle in (0, 180):
            w, h = width, height
            #scroll arrows
            self.arwScrollTop.set_size_request(width, 15)
            self.arwScrollBottom.set_size_request(width, 15)
            self.arwScrollTop.set_alignment(0.5, 1.0)
            self.arwScrollBottom.set_alignment(0.5, 0.0)
            if self.angle == 0:
                self.arwScrollTop.set(gtk.ARROW_UP, gtk.SHADOW_NONE)
                self.arwScrollBottom.set(gtk.ARROW_DOWN, gtk.SHADOW_NONE)
                self.fixd.move(self.arwScrollTop, 0, 0)
                self.fixd.move(self.arwScrollBottom, 0, height - 15)
            else:
                self.arwScrollTop.set(gtk.ARROW_DOWN, gtk.SHADOW_NONE)
                self.arwScrollBottom.set(gtk.ARROW_UP, gtk.SHADOW_NONE)
                self.fixd.move(self.arwScrollBottom, 0, 0)
                self.fixd.move(self.arwScrollTop, 0, height - 15)
        else:
            w, h = height, width
            #scroll arrows
            self.arwScrollTop.set_size_request(15, height)
            self.arwScrollBottom.set_size_request(15, height)
            self.arwScrollTop.set_alignment(1.0, 0.5)
            self.arwScrollBottom.set_alignment(0.0, 0.5)
            if self.angle == 90:
                self.arwScrollTop.set(gtk.ARROW_LEFT, gtk.SHADOW_NONE)
                self.arwScrollBottom.set(gtk.ARROW_RIGHT, gtk.SHADOW_NONE)
                self.fixd.move(self.arwScrollTop, 0, 0)
                self.fixd.move(self.arwScrollBottom, width - 15, 0)
            else:
                self.arwScrollTop.set(gtk.ARROW_RIGHT, gtk.SHADOW_NONE)
                self.arwScrollBottom.set(gtk.ARROW_LEFT, gtk.SHADOW_NONE)
                self.fixd.move(self.arwScrollTop, width - 15, 0)
                self.fixd.move(self.arwScrollBottom, 0, 0)
        #get font size
        font_size = int(self._pango_font_desc.get_size() / pango.SCALE)
        #calc number of rows that will fit (depends on labels font size) and set list_row size
        if self.display_limiters:
            height_modifier = -30
            self._row_height = (h + height_modifier) / self.num_rows
        else:
            height_modifier = 0
        row_modifier = round(((float(h) / pango.SCALE) * 10))
        if ((h + height_modifier) - (font_size * 2)) < font_size:
            self.num_rows = 1
            self._row_height = (h / self.num_rows) - ((h + height_modifier) - (font_size * 2))
        else:
            self.num_rows = (((h + height_modifier) / (font_size * 2)) + int(row_modifier))
            self._row_height = (h / self.num_rows) #reposition rows
        #create labels
        self._create_list_labels()
        if self.angle in (0, 180):
            rw = w
            rh = self._row_height
        else:
            rw = self._row_height
            rh = w
        #move rows into position
        if self.display_limiters:
            c = 15
        else:
            c = 0
        for i in range(self.num_rows):
            self._rows[i][0].set_size_request(rw, rh)
            if self.angle == 0:
                self.fixd.move(self._rows[i][0], 0, c + (i * self._row_height))
            elif self.angle == 90:
                self.fixd.move(self._rows[i][0], c + (i * self._row_height), 0)
            elif self.angle == 180:
                self.fixd.move(self._rows[i][0],
                    0, c + ((self.num_rows - i - 1) * self._row_height))
            else: #270
                self.fixd.move(self._rows[i][0],
                    c + ((self.num_rows - i - 1) * self._row_height), 0)
        #pick hl row
        self._hl_row = int(self.num_rows / 2)
        self._rows[self._hl_row][0].set_visible_window(True)
        self._rows[self._hl_row][1].modify_fg(
            gtk.STATE_NORMAL, self._hl_fg_col)
        #print "num_rows=",self.num_rows, "   _hl_row=", self._hl_row

    def show(self):
        """show"""
        self.fixd.show()

    def hide(self):
        """hide"""
        self.fixd.hide()

    def _on_mouse_button(self, widget, event, idx):
        """mouse button clicked"""
        if self.use_mouse:
            if event.type == gtk.gdk.BUTTON_PRESS:
                if event.button == 1:
                    #left click
                    top_ls_idx = self._ls_idx - self._hl_on_row
                    if (top_ls_idx + idx) != self._ls_idx:
                        self.set_selected(top_ls_idx + idx)
                        #call click callback function
                        if self.signals['mouse-left-click']:
                            self.signals['mouse-left-click'](self._ls_idx)
                elif event.button == 2:
                    #right click
                    if self.signals['mouse-right-click']:
                        self.signals['mouse-right-click'](self, event)
            elif event.type == gtk.gdk._2BUTTON_PRESS:
                #double-click
                if self.signals['mouse-double-click']:
                    self.signals['mouse-double-click']()
        return True

    def _create_container(self):
        """create list container"""
        #create fixed layout to put list labels on
        self.fixd = gtk.Fixed()
        self.fixd.set_size_request(self.width, self.height)
        self.fixd.show()
        #create top & bottom scroll arrows
        self.arwScrollTop = gtk.Arrow(gtk.ARROW_UP, gtk.SHADOW_NONE)
        self.arwScrollBottom = gtk.Arrow(gtk.ARROW_DOWN, gtk.SHADOW_NONE)
        self.arwScrollTop.show()
        self.arwScrollBottom.show()
        self.arwScrollTop.set_alignment(0.5, 1.0)
        self.arwScrollBottom.set_alignment(0.5, 0.0)
        self.arwScrollTop.set_property('visible', False)
        self.arwScrollBottom.set_property('visible', False)
        self.fixd.add(self.arwScrollTop)
        self.fixd.add(self.arwScrollBottom)

    def _create_list_labels(self):
        """create labels as rows"""
        #remove any existing rows
        [self.fixd.remove(row[0]) for row in self._rows]
        #create labels
        self._rows = []
        for i in range(self.num_rows):
            eb = gtk.EventBox()
            lbl = gtk.Label()
            lbl.modify_font(self._pango_font_desc)
            lbl.modify_fg(gtk.STATE_NORMAL, self._fg_col)
            lbl.modify_bg(gtk.STATE_NORMAL, self._hl_bg_col)
            lbl.set_property('xalign', self.properties['xalign'])
            lbl.set_angle(self.angle)
            lbl.show()
            eb.add(lbl)
            eb.add_events(gtk.gdk.BUTTON_PRESS_MASK)
            eb.connect('button-press-event', self._on_mouse_button, i)
            eb.show()
            eb.set_visible_window(False)
            self.fixd.add(eb)
            self._rows.append((eb, lbl))
        #colours
        self.modify_fg(gtk.STATE_NORMAL, self._fg_col)
        self.modify_highlight_bg(gtk.STATE_NORMAL, self._hl_bg_col)

    def set_selected(self, idx_to_select):
        """scroll to and highight given item in list"""
        len_ls = len(self.ls)
        if len_ls == 0:
            self._update_display()
            if self.auto_update:
                self.update()
            return
        #wrap list?
        if idx_to_select < 0:
            if self.wrap_list:
                idx_to_select = len_ls - 1
            else:
                idx_to_select = 0
        if idx_to_select > len_ls - 1:
            if self.wrap_list:
                idx_to_select = 0
            else:
                idx_to_select = len_ls - 1
        #calc direction and gap
        gap = idx_to_select - self._ls_idx
        self._ls_idx = idx_to_select
        if self._ls_idx != self._ls_idx_old:
            self._update_display()
            if self.auto_update:
                self.update()

    def _update_display(self):
        """display the list in the correct position"""
        top_ls_idx = self._ls_idx - self._hl_row
        len_ls = len(self.ls)
        #display scroll limiters?
        if self.display_limiters:
            self.arwScrollTop.set_property('visible', (top_ls_idx > 0))
            self.arwScrollBottom.set_property('visible', (top_ls_idx < (len_ls - self.num_rows)))
            #if len_ls <= self.num_rows and ((top_ls_idx + self._ls_idx) > 0):
            #    self.arwScrollBottom.set_property('visible', False)
            #    self.arwScrollTop.set_property('visible', False)
            #else:
            #    self.arwScrollBottom.set_property('visible', (top_ls_idx < 1))
            #    self.arwScrollTop.set_property('visible',
            #        (top_ls_idx > (len_ls - self.num_rows - 1)))
        #display items
        #print "ls_idx=", self._ls_idx, "  top_ls_idx=", top_ls_idx, "  num_rows=", self.num_rows, "  len(ls)=",len_ls, "  hl_row=",self._hl_row
        for i in range(self.num_rows):
            if (top_ls_idx + i > (len_ls - 1)) or ((top_ls_idx + i) < 0):
                self._rows[i][1].set_text('')
            else:
                self._rows[i][1].set_text(self.ls[top_ls_idx + i])

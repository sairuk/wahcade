# -*- coding: utf-8 -*-
#
###
# Application: wah!cade
# File:        win_history.py
# Description: history viewer file
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
#import os
import sys
import textwrap

#gtk
import pygtk
if sys.platform != 'win32':
    pygtk.require('2.0')
import gtk
#import gobject
import pango

#project modules
from constants import *
from wc_common import WahCade
from mamewah_ini import MameWahIni
from scrolled_list import ScrollList
_ = gettext.gettext


class WinHistory(WahCade):
    """History Window"""

    def __init__(self, WinMain):
        #set main window
        self.WinMain = WinMain
        self.layout_filename = ''
        self.histview_ok = True
        #open history viewer ini
        self.histview_ini = MameWahIni(os.path.join(CONFIG_DIR, 'histview.ini'), 'default', '0.16')
        if os.path.exists(os.path.join(CONFIG_DIR, 'ini', self.WinMain.current_emu + '.his')):
            self.cpviewer_ini = MameWahIni(os.path.join(CONFIG_DIR, 'ini', self.WinMain.current_emu + '.his'), 'default')
        if not os.path.isfile(self.histview_ini.get('history_dat_file')):
            self.WinMain.log_msg("Warning: history file: [%s] does not exist" % (
                self.histview_ini.get('history_dat_file')))
            self.histview_ok = False
        self.layout_filename = self.histview_ini.get('history_layout')
        if not os.path.isfile(self.layout_filename):
            self.WinMain.log_msg("Warning: history layout: [%s] does not exist" % (self.layout_filename))
            self.histview_ok = False
        #build the window
        self.winHistory = gtk.Fixed()
        self.winHistory.set_has_window(True)
        self.imgBackground = gtk.Image()
        self.lblHeading = gtk.Label()
        self.sclHistory = ScrollList()
        self.winHistory.add(self.imgBackground)
        self.winHistory.add(self.make_evb_widget(self.lblHeading))
        self.winHistory.add(self.sclHistory.fixd)
        WinMain.fixd.add(self.winHistory)
        self.imgBackground.show()
        self.lblHeading.show()
        self.winHistory.show()
        #build list
        self.lsHistory = []
        self.sclHistory.auto_update = True
        self.sclHistory.display_limiters = self.WinMain.wahcade_ini.getint('show_list_arrows', 0)
        #widgets
        self._histview_items = [
            (8, self.lblHeading),
            (21, self.sclHistory)]
        #get history
        self.history = self.read_history(self.histview_ini.get('history_dat_file'))
        #app number
        self.app_number = 0

    def set_history(self, rom_name, game_name):
        """display history for rom_name"""
        if not self.histview_ok:
            return
        rom_name = rom_name.upper()
        #display
        self.lsHistory = []
        if rom_name not in self.history:
            self.lblHeading.set_text('no history found')
            self.WinMain.show_window('history')
            return
        tw = textwrap.TextWrapper(width=self.line_length, replace_whitespace=False)
        for line in self.history[rom_name]:
            if line == ' ':
                wrapped_lines = ['']
            else:
                wrapped_lines = tw.wrap(line)
            for wl in wrapped_lines:
                self.lsHistory.append(wl)
        self.sclHistory.ls = self.lsHistory
        self.lblHeading.set_text(game_name)
        self.sclHistory.set_selected(0)
        self.WinMain.show_window('history')

    def read_history(self, dat_filename):
        """read history into dictionary"""
        if not os.path.isfile(dat_filename):
            #self.histview_ok = False
            return
        f = open(dat_filename, 'r')
        d = {}
        while True:
            try:
                line = f.next().strip()
            except StopIteration:
                break
            #start of a game history
            if line[:5] == '$info':
                #history can be for more than one rom
                rom_names = line[6:-1].split(',')
                hist_txt = []
                #read file until end of current game history
                while line != '$end':
                    try:
                        line = f.next().strip()
                    except StopIteration:
                        line = '$end'
                    #add blank lines
                    if line == '':
                        line = ' '
                    if line[0] != '$':
                        hist_txt.append(line)
                if hist_txt != []:
                    for rom_name in rom_names:
                        d[rom_name.upper()] = hist_txt
        #done
        return d

    def load_layout(self, histview_filename):
        """load history viewer layout file"""
        if not os.path.isfile(histview_filename):
            return
        #read file & strip any crap
        lines = open(histview_filename, 'r').readlines()
        lines = [s.strip() for s in lines]
        lines.insert(0, '.')
        #window properties
        hist_width, hist_height = int(lines[1].split(';')[0]), int(lines[2])
        hist_bg_col = gtk.gdk.color_parse(self.get_colour(int(lines[3])))
        self.winHistory.set_size_request(hist_width, hist_height)
        #set window size
        self.winHistory.set_size_request(hist_width, hist_height)
        main_width, main_height = self.WinMain.winMain.get_size_request()
        self.WinMain.fixd.move(self.winHistory,
            ((main_width - hist_width) / 2),
            ((main_height - hist_height) / 2))
        #background
        bg_col = gtk.gdk.color_parse(self.get_colour(int(lines[3])))
        self.winHistory.modify_bg(gtk.STATE_NORMAL, bg_col)
        self.winHistory.move(self.imgBackground, 0, 0)
        self.imgBackground.set_size_request(hist_width, hist_height)
        img_path = self.get_path(lines[4])
        if not os.path.dirname(img_path):
            img_path = os.path.join(os.path.dirname(histview_filename), img_path)
        if os.path.isfile(img_path):
            self.imgBackground.set_property('visible', True)
            self.imgBackground.set_from_file(img_path)
        else:
            self.imgBackground.set_property('visible', False)
        #set all window items
        for offset, widget in self._histview_items:
            #get properties
            d = self.get_layout_item_properties(lines, offset)
            #font
            fd = d['font']
            if d['font-bold']:
                fd += ' Bold'
            if d['font-italic']:
                fd += ' Italic'
            fd += ' %s' % (d['font-size'])
            font_desc = pango.FontDescription(fd)
            #list widget?
            if widget == self.sclHistory:
                hl_bg_col = gtk.gdk.color_parse(self.get_colour(int(lines[6])))
                hl_fg_col = gtk.gdk.color_parse(self.get_colour(int(lines[7])))
                self.sclHistory.modify_highlight_bg(gtk.STATE_NORMAL, hl_bg_col)
                self.sclHistory.modify_highlight_fg(gtk.STATE_NORMAL, hl_fg_col)
            #text colour
            fg_col = gtk.gdk.color_parse(d['text-col'])
            widget.modify_font(font_desc)
            widget.modify_fg(gtk.STATE_NORMAL, fg_col)
            #background colour & transparency
            bg_col = gtk.gdk.color_parse(d['background-col'])
            parent = widget.get_parent()
            if parent.get_ancestor(gtk.EventBox):
                if d['transparent']:
                    parent.set_visible_window(False)
                else:
                    parent.set_visible_window(True)
                    parent.modify_bg(gtk.STATE_NORMAL, bg_col)
            #alignment
            if d['text-align'] == 2:
                widget.set_property('xalign', 0.5)
            else:
                widget.set_property('xalign', d['text-align'])
            #rotation
            try:
                widget.set_angle(d['text-rotation'])
            except AttributeError:
                pass
            #visible?
            #widget.set_property('visible', d['visible'])
            if not d['visible']:
                widget.hide()
                if parent.get_ancestor(gtk.EventBox):
                    parent.hide()
            else:
                widget.show()
                if parent.get_ancestor(gtk.EventBox):
                    parent.show()
            #size
            widget.set_size_request(d['width'], d['height'])
            #list?
            if widget == self.sclHistory:
                widget = self.sclHistory.fixd
                #setup font info for history list
                context = self.sclHistory._rows[0][1].get_pango_context()
                metrics = context.get_metrics(font_desc)
                char_width = pango.PIXELS(metrics.get_approximate_char_width())
                self.line_length = (d['width'] / (char_width + 2))
            elif parent.get_ancestor(gtk.EventBox):
                widget = widget.get_parent()
            #move on fixed layout
            self.winHistory.move(widget, d['x'], d['y'])

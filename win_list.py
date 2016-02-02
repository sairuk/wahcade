#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
###
# Application: wah!cade
# File:        win_list.py
# Description: Wah!Cade Setup - Edit Games List window
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

from constants import *
from glade2 import *
from mamewah_ini import MameWahIni
from wc_common import WahCade
import filters
_ = gettext.gettext


class WinList(GladeSupport, WahCade):
    """wahcade setup - edit list window"""
    NUM_COLS = 13

    def __init__(self, glade_filename, window_name, emu_name, emu_list_idx):
        """build the window"""
        WahCade.__init__(self)
        GladeSupport.__init__(self, glade_filename, window_name, APP_NAME)
        self.config_dir = CONFIG_DIR
        self.emu_name = emu_name
        self.emu_list_idx = emu_list_idx
        #games list
        self.tvwList, self.lsList, self.tvwsList = self.setup_treeview(
            columns = [
                'Game Name',
                'ROM Name',
                'Year',
                'Manufacturer',
                'Clone Of',
                'Rom Of',
                'Display Type',
                'Screen Type',
                'Controller Type',
                'Driver Status',
                'Colour Status',
                'Sound Status',
                'Category'],
            column_types = [gobject.TYPE_STRING] * self.NUM_COLS,
            container = self.scwList,
            edit_cell_cb = self.on_tvwList_edited,
            resizeable_cols = True,
            highlight_rows = False)
        #self.tvwList.connect('row-activated', self.on_tvwList_activated)
        self.tvwList.connect('key-release-event', self.on_tvwList_key_event)
        #activate multiple selection mode on tvwsList
        self.tvwsList.set_mode(gtk.SELECTION_MULTIPLE)
        #load lists
        i = 0
        emu_game_lists = []
        while True:
            ini_file = os.path.join(self.config_dir, 'ini', '%s-%s.ini' % (self.emu_name, i))
            if os.path.isfile(ini_file):
                list_ini = MameWahIni(ini_file)
                emu_game_lists.append(list_ini.get('list_title'))
                i += 1
            else:
                break
        l = ['%s: %s' % (i, r) for i, r in enumerate(emu_game_lists)]
        self.setup_combo_box(self.cboList, l)
        #setup filters & emu ini
        emu_ini_filename = os.path.join(self.config_dir, 'ini', '%s.ini' % (self.emu_name))
        if os.path.isfile(emu_ini_filename):
            self.emu_ini = MameWahIni(emu_ini_filename)
            #filters._mameinfo_file = os.path.join(self.emu_ini.get('dat_file'))
            filters._catver_ini = os.path.join(self.emu_ini.get('catver_ini_file'))
        else:
            print _("Error: Emulator Ini file: [%s] doesn't exist" % (emu_ini_filename))
        #get ini files
        self.wahcade_ini = MameWahIni(os.path.join(self.config_dir, 'wahcade.ini'))
        #window size
        self.do_events()
        w, h = self.wahcade_ini.get('setup_window_size', 'default', '400x400').split('x')
        self.winList.resize(width=int(w), height=int(h))
        #load filter
        self.new_iter = None
        self.new_path = None
        self.new_col = 0
        self.list_altered = False
        self.cboList.set_active(self.emu_list_idx)

    def on_winList_delete_event(self, *args):
        """window closed"""
        self.save_list_query()
        #close window
        self.winList.destroy()
        return False

    def on_btnAdd_clicked(self, *args):
        """add a new row"""
        self.new_iter = self.lsList.append(([''] * self.NUM_COLS))
        self.new_path = self.lsList.get_path(self.new_iter)
        self.new_col = 0
        tvc = self.tvwList.get_column(0)
        self.tvwList.set_cursor(self.new_path, tvc, True)

    def on_btnRemove_clicked(self, *args):
        """remove selected rows"""
        rows2remove = []
        self.tvwsList.selected_foreach(self.remove_selected, rows2remove)
        if len(rows2remove) > 0:
            for row in rows2remove:
               self.lsList.remove(row)
            self.update_total_games()
            self.list_altered = True

    def remove_selected(self, model, path, iter, data=None):
        """remove selected rows from list"""
        data.append(iter)

    def on_btnSave_clicked(self, *args):
        """save"""
        filters.write_filtered_list(
            self.list_filename,
            self.lsList)
        self.list_altered = False

    def on_btnClose_clicked(self, *args):
        """close"""
        self.on_winList_delete_event()

    def on_tvwList_key_event(self, widget, event, *args):
        """keyboard event on list"""
        if event.type == gtk.gdk.KEY_RELEASE:
            #keyboard pressed, get gtk keyname
            keyname = gtk.gdk.keyval_name(event.keyval).lower()
            if keyname == 'tab' and self.new_iter and self.new_path:
                self.new_col += 1
                if self.new_col >= self.NUM_COLS:
                    self.new_col = 0
                tvc = self.tvwList.get_column(self.new_col)
                self.tvwList.scroll_to_cell(self.new_path, tvc)
                self.tvwList.set_cursor(self.new_path, tvc, True)

    def on_tvwList_edited(self, cell, path, new_text, user_data, *args):
        """list edited"""
        ls, col = user_data
        if col == 0 and new_text == '':
            dlg = gtk.MessageDialog(
                self.winList,
                gtk.DIALOG_MODAL,
                gtk.MESSAGE_ERROR,
                gtk.BUTTONS_CLOSE,
                _('You must set a rom name'))
            resp = dlg.run()
            dlg.destroy()
        else:
            #set
            self.list_altered = True
            ls[path][col] = new_text
        self.update_total_games()

    def on_cboList_changed(self, *args):
        """emulator list combo"""
        #get settings for current emu list
        self.save_list_query()
        self.emu_list_idx = self.cboList.get_active()
        if self.emu_list_idx >= 0:
            self.load_list()

    def load_list(self):
        """load games list"""
        #clear games list
        self.lsList.clear()
        #set filename
        self.list_filename = os.path.join(
            self.config_dir,
            'files',
            '%s-%s.lst' % (self.emu_name, self.emu_list_idx))
        #load list (if it exists)
        if os.path.isfile(self.list_filename):
            games_list, games_list_len = filters.read_filtered_list(self.list_filename)
            games_list.sort()
            [self.lsList.append(r) for r in games_list]
            self.update_total_games()
        elif self.emu_list_idx == 0:
            print _('Please Wait. Creating initial filter...')
            #self.message.display_message(_('Please Wait'), _('Creating initial filter...'))
            #self.list_creation_attempted = True
            #self.do_events()
            filters.create_initial_filter(
                self.emu_ini.get('dat_file'),
                os.path.join(
                    self.config_dir,
                    'files',
                    '%s-0.ftr' % (self.emu_name)),
                self.list_filename,
                self.emu_ini)
            self.load_list()

    def save_list_query(self):
        """prompt to save changes if necessary"""
        if self.list_altered:
            dlg = gtk.MessageDialog(
                self.winList,
                gtk.DIALOG_MODAL,
                gtk.MESSAGE_QUESTION,
                gtk.BUTTONS_YES_NO,
                _('Save List changes?'))
            resp = dlg.run()
            if resp == gtk.RESPONSE_YES:
                self.on_btnSave_clicked()
            dlg.destroy()
            return True
        else:
            return False

    def update_total_games(self):
        """Refresh the total number of the games"""
        self.lblTotalGames.set_text(_('%s games' % (len(self.lsList))))

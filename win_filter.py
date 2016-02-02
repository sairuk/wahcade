#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
###
# Application: wah!cade
# File:        win_filter.py
# Description: Wah!Cade Setup Mame Filters window
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


class DlgWait(GladeSupport, WahCade):
    """wahcade filter setup - wait dialog"""

    def __init__(self, glade_filename, window_name, lblwait=None):
        """build the dialog"""
        GladeSupport.__init__(self, glade_filename, window_name, APP_NAME)
        if lblwait is not None:
            self.lblWait.set_label(lblwait)

    def on_btnCancel_clicked(self, *args):
        """cancel clicked"""
        pass

    def on_dlgWait_delete_event(self, *args):
        """close dialog"""
        return True


class WinFilter(GladeSupport, WahCade):
    """wahcade setup - set filter window"""

    def __init__(self, glade_filename, window_name, emu_name):
        """build the window"""
        WahCade.__init__(self)
        GladeSupport.__init__(self, glade_filename, window_name, APP_NAME)
        self.config_dir = CONFIG_DIR
        #print "emu_name=",emu_name
        self.emu_name = emu_name
        self.emu_list_idx = 0
        #setup tree & lists
        self.tsFilter = gtk.TreeStore(str, gobject.TYPE_BOOLEAN, str)
        self.tvwFilter = gtk.TreeView(model = self.tsFilter)
        #text col
        cellrt = gtk.CellRendererText()
        tvcol = gtk.TreeViewColumn(_('Filter'))
        tvcol.pack_start(cellrt, True)
        tvcol.add_attribute(cellrt, 'text', 0)
        tvcol.set_resizable(True)
        #checkbox col
        crt = gtk.CellRendererToggle()
        crt.set_property('activatable', True)
        crt.connect('toggled', self.on_tvwFilter_toggled, self.tsFilter)
        tvcol2 = gtk.TreeViewColumn(_('Selected?'), crt)
        tvcol2.add_attribute(crt, 'active', 1)
        #add columns to treeview
        self.tvwFilter.append_column(tvcol)
        self.tvwFilter.append_column(tvcol2)
        #self.tvwFilter.set_rules_hint(True)
        self.tvwFilter.show()
        self.scwFilter.add(self.tvwFilter)
        #games list
        self.tvwGames, self.lsGames, self.tvwsGames = self.setup_treeview(
            columns = ['Games'],
            column_types = [gobject.TYPE_STRING],
            container = self.scwGameList,
            resizeable_cols = True,
            highlight_rows = False)
        #filter values
        self._display_clones = [
            [_('No'), 'no'],
            [_('Yes'), 'yes'],
            [_('Only if better than Parent'), 'better']]
        self._filter_sections = [
            ['filter_type', _('Display Clones')],
            ['year', _('Year Filters')],
            ['manufacturer', _('Manufacturer Filters')],
            ['driver', _('BIOS Filters')],
            ['display_type', _('Screen Type Filters')],
            ['screen_type', _('Screen Orientation Filters')],
            ['controller_type', _('Input Type Filters')],
            ['driver_status', _('General Status Filters')],
            ['colour_status', _('Colour Status Filters')],
            ['sound_status', _('Sound Status Filters')],
            ['category', _('Category Filters')]]
        #load lists
        i = 0
        emu_game_lists = []
        while True:
            ini_file = os.path.join(CONFIG_DIR, 'ini', '%s-%s.ini' % (self.emu_name, i))
            if os.path.isfile(ini_file):
                list_ini = MameWahIni(ini_file)
                emu_game_lists.append(list_ini.get('list_title'))
                i += 1
            else:
                break
        l = ['%s: %s' % (i, r) for i, r in enumerate(emu_game_lists)]
        
        #setup filters & emu ini
        emu_ini_filename = os.path.join(CONFIG_DIR, 'ini', '%s.ini' % (self.emu_name))
        if os.path.isfile(emu_ini_filename):
            self.emu_ini = MameWahIni(emu_ini_filename)
            #filters._mameinfo_file = os.path.join(self.emu_ini.get('dat_file'))
            filters._catver_ini = os.path.join(self.emu_ini.get('catver_ini_file'))
        else:
            print _("Error: Emulator Ini file: [%s] doesn't exist" % (emu_ini_filename))       
        self.setup_combo_box(self.cboLists, l)
        #load filter
        self.cboLists.set_active(self.emu_list_idx)
        self.filter_altered = False

    def on_winFilter_delete_event(self, *args):
        """window closed"""
        if self.filter_altered:
            dlg = gtk.MessageDialog(
                self.winFilter,
                gtk.DIALOG_MODAL,
                gtk.MESSAGE_QUESTION,
                gtk.BUTTONS_YES_NO,
                _('Save filter changes?'))
            resp = dlg.run()
            if resp == gtk.RESPONSE_YES:
                self.on_btnSaveFilter_clicked()
            dlg.destroy()
        #close window
        self.winFilter.destroy()
        return False

    def on_tvwFilter_toggled(self, cell, path, model, *args):
        """filter item checkbox toggled"""
        #don't change list 0 settings
        if self.emu_list_idx == 0:
            return
        #parent?
        if model[path].parent:
            self.filter_altered = True
            #toggle filter item
            filter_section = model[path].parent[2]
            filter_item = model[path][0]
            if filter_section != 'filter_type':
                model[path][1] = not model[path][1]
                self.current_filter[filter_section][filter_item] = model[path][1]
            else:
                #set filter type
                if model[path][1]:
                    return
                model[path][1] = not model[path][1]
                self.current_filter['filter_type'] = model[path][2]
                #toggle update other items
                for subrow in model[path].parent.iterchildren():
                    if subrow[2] != model[path][2]:
                        subrow[1] = not model[path][1]
        else:
            #toggle all items in section
            filter_section = model[path][2]
            if filter_section != 'filter_type':
                model[path][1] = not model[path][1]
                self.filter_altered = True
                #update all children with new value
                for subrow in model[path].iterchildren():
                    subrow[1] = model[path][1]
                #toggle actual filter
                for filter_item in self.current_filter[filter_section]:
                    self.current_filter[filter_section][filter_item] = model[path][1]

    def on_btnApplyFilter_clicked(self, *args):
        """generate the current filter"""
        self.set_busy_cursor(self.winFilter)
        #save first?
        if self.filter_altered:
            self.on_btnSaveFilter_clicked()
        #recreate initial filter?
        if self.emu_list_idx == 0:
            self.create_initial_filter()
        else:
            #create list from the just saved filter
            filters.create_filtered_list(
                os.path.join(CONFIG_DIR, 'files', '%s-0.lst' % (self.emu_name)),
                self.current_filter,
                os.path.join(
                    CONFIG_DIR,
                    'files',
                    '%s-%s.lst' % (self.emu_name, self.emu_list_idx)))
        #done - reload list
        self.load_list()
        self.set_normal_cursor(self.winFilter)

    def on_btnReset_clicked(self, *args):
        """reset the current filter"""
        #load filter 0
        old_idx = self.emu_list_idx
        self.emu_list_idx = 0
        self.load_filter()
        self.emu_list_idx = old_idx
        self.enable_buttons()

    def on_btnSaveFilter_clicked(self, *args):
        """save the current filter"""
        #save current filter
        filters.write_filter(
            self.current_filter,
            os.path.join(
                CONFIG_DIR,
                'files',
                '%s-%s.ftr' % (self.emu_name, self.emu_list_idx)))
        self.filter_altered = False

    def on_btnClose_clicked(self, *args):
        """save the current filter & close window"""
        self.on_winFilter_delete_event()

    def on_cboLists_changed(self, *args):
        """emulator list combo"""
        #get settings for current emu list
        self.emu_list_idx = self.cboLists.get_active()
        emu_list_ini = MameWahIni(os.path.join(CONFIG_DIR, 'ini', '%s-%s.ini' % (self.emu_name, self.emu_list_idx)))
        if self.emu_list_idx >= 1:
            if emu_list_ini.get('list_type') != 'normal':
                self.show_msg_dialog(msg=_('List Type must be "normal" to generate filters'))
                self.cboLists.set_active(0)
                return
        if self.emu_list_idx >= 0:
            self.load_filter()

    def load_filter(self):
        """load filter"""
        #clear filter list
        self.tsFilter.clear()
        i = 0
        #find filter file
        filter_file = os.path.join(
            CONFIG_DIR,
            'files',
            '%s-%s.ftr' % (self.emu_name, self.emu_list_idx))
        if not os.path.isfile(filter_file):
            #filter doesn't exist, so try and use use filter for list 0
            filter_file = os.path.join(CONFIG_DIR, 'files', '%s-0.ftr' % (self.emu_name))
            if not os.path.isfile(filter_file):
                #list 0 file doesn't exist either, generate one
                self.create_initial_filter()
        #read filter
        self.current_filter = filters.read_filter(filter_file)
        if not self.current_filter:
            #invalid filter, try creating one
            self.create_initial_filter()
        #for each section in filters
        for fk in self._filter_sections:
            #add filter section title
            parent_iter = self.tsFilter.append(None, [fk[1], False, fk[0]])
            if fk[0] == 'filter_type':
                #add "display clones" filter
                for idx, ft_row in enumerate(self._display_clones):
                    #print "idx, ft_row, self.current_filter[fk[0]]=",idx, ft_row, self.current_filter[fk[0]]
                    if self.current_filter[fk[0]] == str(idx):
                        yesno = True
                    else:
                        yesno = False
                    self.tsFilter.append(parent_iter, [ft_row[0], yesno, idx])
            else:
                #add other filter sections
                sorted_keys = self.current_filter[fk[0]].keys()
                sorted_keys.sort()
                for ft_row in sorted_keys:
                    self.tsFilter.append(parent_iter, [ft_row, self.current_filter[fk[0]][ft_row], ''])
        #load the games list
        self.load_list()
        self.enable_buttons()

    def enable_buttons(self):
        """enable / disable buttons"""
        if self.emu_list_idx == 0:
            self.btnSaveFilter.set_sensitive(False)
            self.btnReset.set_sensitive(False)
        else:
            self.btnSaveFilter.set_sensitive(True)
            self.btnReset.set_sensitive(True)

    def create_initial_filter(self):
        """create the initial (mame-0.ftr) filter"""
        #show message
        self.DlgWait = DlgWait(SETUP_GLADE_FILE, 'dlgWait')
        #create initial filer
        list_filename = os.path.join(CONFIG_DIR, 'files', '%s-0.lst' % (self.emu_name))
        self.do_events()
        filters.create_initial_filter(
            self.emu_ini.get('dat_file'),
            os.path.join(
                CONFIG_DIR,
                'files',
                '%s-0.ftr' % (self.emu_name)),
            list_filename,
            self.emu_ini,
            self.dlgwait_pulse)
        self.DlgWait.dlgWait.destroy()

    def dlgwait_pulse(self):
        """pulse the dlgWait progress bar"""
        self.DlgWait.pgbWait.pulse()
        self.do_events()

    def load_list(self):
        """load games list"""
        #clear games list
        self.lsGames.clear()
        self.lblTotalGames.set_text(_('No Games'))
        #set filename
        list_filename = os.path.join(
            CONFIG_DIR,
            'files',
            '%s-%s.lst' % (self.emu_name, self.emu_list_idx))
        #load list (if it exists)
        if os.path.isfile(list_filename):
            games_list, games_list_len = filters.read_filtered_list(list_filename)
            self.lblTotalGames.set_text(_('%s games' % (games_list_len)))
            gl = [l[0] for l in games_list]
            gl.sort()
            for row in gl:
                self.lsGames.append((row, ))

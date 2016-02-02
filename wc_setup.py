# -*- coding: UTF-8 -*-
#
###
# Application: wah!cade
# File:        wc_setup.py
# Description: Wah!Cade Setup Application
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
import glob
import shutil
from subprocess import Popen

from constants import *
from glade2 import *
from mamewah_ini import MameWahIni
from key_consts import mamewah_keys
from wc_common import WahCade
from win_filter import WinFilter, DlgWait
from win_list import WinList
import joystick
_ = gettext.gettext

_mouse_ctrls = {
    _('Mouse Button 1'): ['MOUSE_BUTTON0'],
    _('Mouse Button 2'): ['MOUSE_BUTTON1'],
    _('Mouse Button 3'): ['MOUSE_BUTTON2'],
    _('Mouse Button 4'): ['MOUSE_BUTTON3'],
    _('Mouse Button 5'): ['MOUSE_BUTTON4'],
    _('Mouse Button 6'): ['MOUSE_BUTTON5'],
    _('Mouse Button 7'): ['MOUSE_BUTTON6'],
    _('Mouse Button 8'): ['MOUSE_BUTTON7'],
    _('Mouse Button 9'): ['MOUSE_BUTTON8'],
    _('Mouse Left'): ['MOUSE_LEFT'],
    _('Mouse Right'): ['MOUSE_RIGHT'],
    _('Mouse Up'): ['MOUSE_UP'],
    _('Mouse Down'): ['MOUSE_DOWN'],
    _('Scroll Wheel Down'): ['MOUSE_SCROLLDOWN'],
    _('Scroll Wheel Up'): ['MOUSE_SCROLLUP']}


class DlgAddEmu(GladeSupport, WahCade):
    """wahcade setup - add new emulator"""

    def __init__(self, glade_filename, window_name, WinSetup):
        """build the dialog"""
        GladeSupport.__init__(self, glade_filename, window_name, APP_NAME)
        self.dlgAddEmu.set_transient_for(WinSetup.winSetup)
        self.dlgAddEmu.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        #winsetup class
        self.WinSetup = WinSetup
        #create new emulator list
        self.tvw, self.ls, self.tvws = self.setup_treeview(
            columns = [_('Select an Emulator Template...')],
            column_types = [gobject.TYPE_STRING, gobject.TYPE_STRING,
                gobject.TYPE_STRING],
            container = self.scw,
            resizeable_cols = False)
        #get list of available templates
        emu_ini_files = glob.glob(os.path.join(APP_PATH, 'templates', '*.ini'))
        for emu_ini in emu_ini_files:
            ini = MameWahIni(emu_ini)
            if not ini.has_option('list_title'):
                basename = os.path.splitext(os.path.basename(emu_ini))[0]
                self.ls.append(
                    ('%s (%s)' % (ini.get('emulator_title'), basename),
                    basename,
                    emu_ini))
        #set dialog size
        num = len(self.ls)
        if num > 10:
            num = 10
        self.dlgAddEmu.set_size_request(320, 120 + (num * 15))
        #sort
        self.ls.set_sort_column_id(0, gtk.SORT_ASCENDING)

    def on_btnCancel_clicked(self, *args):
        """cancel clicked"""
        self.dlgAddEmu.destroy()

    def on_btnOk_clicked(self, *args):
        """OK clicked"""
        tvwIter = self.tvws.get_selected()[1]
        if tvwIter:
            emu = self.ls.get_value(tvwIter, 1)
            default_filename = os.path.join(
                CONFIG_DIR, 'ini', '%s.ini' % emu)
            if os.path.exists(default_filename):
                #display save emulator .ini file as... dialog
                dlg = gtk.FileChooserDialog(
                    title = _('Save Emulator File'),
                    action = gtk.FILE_CHOOSER_ACTION_SAVE,
                    buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                        gtk.STOCK_SAVE_AS, gtk.RESPONSE_OK))
                ftr = gtk.FileFilter()
                ftr.set_name('All files')
                ftr.add_pattern('*')
                dlg.add_filter(ftr)
                ftr = gtk.FileFilter()
                ftr.set_name('Ini files')
                ftr.add_pattern('*.ini')
                dlg.add_filter(ftr)
                dlg.set_filter(ftr)
                if gtk.check_version(2, 8, 0) is None:
                    try:
                        dlg.set_do_overwrite_confirmation(True)
                    except AttributeError:
                        pass
                dlg.set_current_folder(os.path.dirname(default_filename))
                dlg.set_current_name(os.path.basename(default_filename))
                response = dlg.run()
                if response == gtk.RESPONSE_OK:
                    #save
                    dest = dlg.get_filename()
                    if os.path.isfile(dest):
                        #exists, so don't copy
                        dlg = gtk.MessageDialog(
                            self.dlgAddEmu,
                            gtk.DIALOG_MODAL,
                            gtk.MESSAGE_ERROR,
                            gtk.BUTTONS_OK,
                            _('Emulator already exists!'))
                        resp = dlg.run()
                        dlg.destroy()
                    else:
                        #copy to ini files
                        dest_ini_name = os.path.basename(os.path.splitext(dest)[0])
                        self.WinSetup.create_new_emulator_files(emu, dest_ini_name)
                        self.dlgAddEmu.destroy()
                dlg.destroy()
            else:
                #copy to ini files
                dest_ini_name = os.path.basename(os.path.splitext(default_filename)[0])
                self.WinSetup.create_new_emulator_files(emu, dest_ini_name)
                self.dlgAddEmu.destroy()


class DlgKeyPress(GladeSupport, WahCade):
    """wahcade setup - key press dialog"""

    def __init__(self, glade_filename, window_name, tvw_path, key_changed_cb, joystick):
        """build the dialog"""
        GladeSupport.__init__(self, glade_filename, window_name, APP_NAME)
        #setup
        self.key_changed_cb = key_changed_cb
        self.joystick = joystick
        self.tvw_path = tvw_path
        #mouse controls
        mouse_ctrls = _mouse_ctrls.keys()
        mouse_ctrls.sort()
        self.setup_combo_box(self.cboMouse, mouse_ctrls)
        #joystick controls
        if self.joystick:
            self.rev_joystick_ctrls = dict([(v, k) for (k, v) in joystick.ctrls.iteritems()])
            if joystick.poll:
                self.event_source = gobject.timeout_add(
                    50, joystick.poll, self.on_cboJoystick_key_press_event, 100000)
            else:
                self.event_source = None
            joystick_ctrls = joystick.ctrls.keys()
            joystick_ctrls.sort()
            self.setup_combo_box(self.cboJoystick, joystick_ctrls)

    def on_cboMouse_changed(self, *args):
        """mouse ctrl selected"""
        if self.cboMouse.get_active() >= 0:
            keyname = self.cboMouse.get_model()[self.cboMouse.get_active()][0]
            mw_keys = _mouse_ctrls[keyname]
            #print "mouse selected:", keyname, ', ', mw_keys
            self.dlgKeyPress.destroy()
            self.key_changed_cb(self.tvw_path, mw_keys, keyname)

    def on_cboJoystick_changed(self, *args):
        """joystick ctrl selected"""
        if self.cboJoystick.get_active() >= 0:
            keyname = self.cboJoystick.get_model()[self.cboJoystick.get_active()][0]
            mw_keys = [self.joystick.ctrls[keyname]]
            #print "joy selected:", keyname, ', ', mw_keys
            self.dlgKeyPress.destroy()
            self.key_changed_cb(self.tvw_path, mw_keys, keyname)

    def on_btnClear_clicked(self, *args):
        """clear clicked"""
        self.dlgKeyPress.destroy()
        self.key_changed_cb(self.tvw_path, [], '')

    def on_btnCancel_clicked(self, *args):
        """cancel clicked"""
        self.dlgKeyPress.destroy()

    def on_cboJoystick_key_press_event(self, widget, event, *args):
        """a joystick action has been pressed"""
        joystick_key = None
        if len(args) > 1:
            if args[0] == "JOYSTICK":
                joystick_key = args[1]
        if event.type == gtk.gdk.KEY_PRESS and joystick_key:
            keyname = joystick_key
            self.lblJoystick.set_text(self.rev_joystick_ctrls[joystick_key])
            self.do_events()

    def on_txeKey_key_press_event(self, widget, event, *args):
        """a key has been pressed"""
        mw_keys = []
        if event.type == gtk.gdk.KEY_PRESS:
            #keyboard pressed, get gtk keyname
            keyname = gtk.gdk.keyval_name(event.keyval).lower()
            #get mamewah keyname
            if keyname in mamewah_keys:
                mw_keys = mamewah_keys[keyname]
        else:
            return
        #got something valid?
        if keyname == '' or mw_keys == []:
            #unrecognized / unmapped key / mouse
            dlg = gtk.MessageDialog(
                self.dlgKeyPress,
                gtk.DIALOG_MODAL,
                gtk.MESSAGE_WARNING,
                gtk.BUTTONS_OK,
                _('Could not recognize key'))
            resp = dlg.run()
            dlg.destroy()
            return
        if len(mw_keys) > 0:
            #update list
            self.dlgKeyPress.destroy()
            self.key_changed_cb(self.tvw_path, mw_keys, keyname)


class WinSetup(GladeSupport, WahCade):
    """wahcade setup - main window"""

    def __init__(self, glade_filename, window_name, config_opts, config_args):
        """build the window"""
        WahCade.__init__(self)
        GladeSupport.__init__(self, glade_filename, window_name, APP_NAME)
        #command-line options
        self.config_opts = config_opts
        #set default config location (create / update as necessary)
        self.config_dir = CONFIG_DIR
        if not os.path.exists(self.config_dir):
            self.copy_user_config('all')
        else:
            #update current config
            self.copy_user_config()
        #keys list
        self.tvwKeys, self.lsKeys, self.tvwsKeys = self.setup_treeview(
            columns = ['Function', 'Key'],
            column_types = [gobject.TYPE_STRING, gobject.TYPE_STRING],
            container = self.scwKeys,
            resizeable_cols = False)
        self.lsKeys.set_sort_column_id(0, gtk.SORT_ASCENDING)
        self.tvwKeys.connect('row-activated', self.on_tvwKeys_row_activated)
        self.tvwKeys.set_tooltip_text(_('Double-Click a row to change a Key...'))
        #set max width for keys column (stops window getting too wide)
        col = self.tvwKeys.get_column(1)
        col.set_max_width(200)
        #get ini files
        self.wahcade_ini = MameWahIni(os.path.join(self.config_dir, 'wahcade.ini'))
        self.histview_ini = MameWahIni(os.path.join(self.config_dir, 'histview.ini'))
        self.cpviewer_ini = MameWahIni(os.path.join(self.config_dir, 'cpviewer.ini'))
        self.ctrlr_ini = MameWahIni(os.path.join(self.config_dir, 'ctrlr', 'default.ini'), 'ctrlr')
        #emu stuff
        self.emu_list_gen_types = [
            [['rom_folder'], 'Rom Directory'],
            [['rom_folder_vs_listxml', 'list_xml'], 'XML File'],
            [['rom_folder_vs_dat_file', 'dat_file'], 'DAT File']]
        self.emu_scrsave_types = [
            ['blank_screen', 'Blank Screen'],
            ['slideshow', 'Slide Show'],
            ['movie', 'Movies'],
            ['launch_scr', 'Launch External Screen Saver']]
        self.emu_list_types = [
            ['normal', 'Normal'],
            ['most_played', 'Most Played'],
            ['longest_played', 'Longest Played']]
        self.music_movie_mix = [
            ['mute_movies', 'Mute Movies'],
            ['merge', 'Mix with Music']]
        self.emu_artwork_txe = [
            self.txeEmuArt1, self.txeEmuArt2, self.txeEmuArt3, self.txeEmuArt4,
            self.txeEmuArt5, self.txeEmuArt6, self.txeEmuArt7, self.txeEmuArt8,
            self.txeEmuArt9, self.txeEmuArt10]
        self.emu_artwork_btn = [
            self.btnEmuArt1, self.btnEmuArt2, self.btnEmuArt3, self.btnEmuArt4,
            self.btnEmuArt5, self.btnEmuArt6, self.btnEmuArt7, self.btnEmuArt8,
            self.btnEmuArt9, self.btnEmuArt10]
        #setup combo boxes
        self.setup_combo_box(self.cboEmuScrSaver, [r[1] for r in self.emu_scrsave_types])
        self.setup_combo_box(self.cboEmuListGen, [r[1] for r in self.emu_list_gen_types])
        self.setup_combo_box(self.cboEmuListType, [r[1] for r in self.emu_list_types])
        self.setup_combo_box(self.cboWCMovieMix, [r[1] for r in self.music_movie_mix])
        #global joy
        self.joystick = joystick.joystick()
        self.joystick.use_all_controls()
        #get default window size & pos
        self.do_events()
        w, h = self.wahcade_ini.get('setup_window_size', 'default', '400x400').split('x')
        self.winSetup.resize(width=int(w), height=int(h))
        #load settings
        self.load_settings()
        self.setup_altered = False
        #set icon sizes
        settings = gtk.settings_get_default()
        settings.set_string_property('gtk-icon-sizes', 'gtk-button=16,16', '')

    def on_winSetup_delete_event(self, *args):
        """done, quit the application"""
        #save settings
        self.save_setups()
        #save default window size & pos
        win_size = self.winSetup.get_size()
        self.wahcade_ini.set('setup_window_size', '%sx%s' % (win_size))
        self.wahcade_ini.write()
        #exit gtk loop
        gtk.main_quit()
        return False

    def on_Setup_changed(self, widget, *args):
        """widget has been modified, update altered flag"""
        self.setup_altered = True

    def on_mnuFSave_activate(self, *args):
        """save settings"""
        self.save_setups(False)

    def on_mnuFReset_activate(self, *args):
        """reset settings"""
        dlg = gtk.MessageDialog(
            self.winSetup,
            gtk.DIALOG_MODAL,
            gtk.MESSAGE_QUESTION,
            gtk.BUTTONS_YES_NO,
            _('Are you sure you want to revert to the default settings?'))
        resp = dlg.run()
        if resp == gtk.RESPONSE_YES:
            #delete and recreate settings dir
            shutil.rmtree(self.config_dir, True)
            self.copy_user_config('all')
            #reload settings
            self.load_settings()
            self.setup_altered = False
        dlg.destroy()

    def on_mnuFResetFilters_activate(self, *args):
        """reset file filters"""
        dlg = gtk.MessageDialog(
            self.winSetup,
            gtk.DIALOG_MODAL,
            gtk.MESSAGE_QUESTION,
            gtk.BUTTONS_YES_NO,
            _('Are you sure you want to reset the file filters?'))
        resp = dlg.run()
        if resp == gtk.RESPONSE_YES:
            #delete the ~/.wahcade/files dir
            shutil.rmtree(os.path.join(self.config_dir, 'files'), True)
            self.copy_user_config()
            #reload settings
            #self.load_settings()
            #self.setup_altered = False
        dlg.destroy()

    def on_mnuFQuit_activate(self, *args):
        """quit"""
        self.on_winSetup_delete_event()

    def on_mnuHAbout_activate(self, *args):
        """about dialog"""
        self.show_about_dialog('Wah!Cade Setup', self.config_dir)

    def on_tvwKeys_row_activated(self, widget, path, column):
        """keys list double-clicked"""
        #show key press dialog
        dlg = DlgKeyPress(
            SETUP_GLADE_FILE,
            'dlgKeyPress',
            path,
            self.on_tvwKeys_change,
            self.joystick)

    def on_tvwKeys_change(self, path, mw_keys, keyname):
        """update key list with new keyname"""
        #print "on_tvwKeys_change=",path, mw_keys, keyname
        #clear
        if mw_keys == [] and keyname == '':
            self.ctrlr_ini.set(self.lsKeys[path][0], '')
            self.lsKeys[path][1] = ''
            return
        #get existing actions for key
        mw_functions = self.ctrlr_ini.reverse_get(mw_keys[0])
        if mw_functions != []:
            #re-assign?
            key_actions = ''
            for f in mw_functions:
                key_actions += '\t%s\n' % f
            msg = _('"%s" is already assigned to the following actions:\n%s\n' % (
                keyname.upper(),
                key_actions))
            msg += _('Keep existing assignments?')
            dlg = gtk.MessageDialog(
                self.winSetup,
                gtk.DIALOG_MODAL,
                gtk.MESSAGE_QUESTION,
                gtk.BUTTONS_YES_NO,
                msg)
            resp = dlg.run()
            dlg.destroy()
            if resp == gtk.RESPONSE_NO:
                #remove from each old assignment
                for mrf in mw_functions:
                    v = self.ctrlr_ini.get(mrf)
                    lv = v.strip(' "').split(' | ')
                    lv.remove(mw_keys[0])
                    s = ''
                    for v in lv:
                        s = '%s | ' % v
                    if lv != []:
                        s = '"%s"' % s[:-3]
                    self.ctrlr_ini.set(mrf, s)
        #update keys for selected action
        existing_keys = self.ctrlr_ini.get(self.lsKeys[path][0])
        if existing_keys == '':
            self.ctrlr_ini.set(self.lsKeys[path][0], '"%s"' % mw_keys[0])
        else:
            self.ctrlr_ini.set(
                self.lsKeys[path][0],
                '"%s | %s"' % (existing_keys.strip('"'), mw_keys[0]))
        self.setup_altered = True
        #redisplay list
        self.populate_keys()

    def on_cboEmu_changed(self, *args):
        """emulator combo"""
        #save current emulator settings?
        if self.current_emu:
            self.save_emulator_settings()
            if self.current_emu_list:
                #save emu list settings
                self.save_emulator_list_settings()
                self.current_emu_list = None
        #change to new emulator
        if self.cboEmu.get_active() >= 0:
            self.current_emu = self.emu_lists[self.cboEmu.get_active()]
            self.load_emulator_settings(self.current_emu[1], self.current_emu[2])

    def on_txeEmuTitle_changed(self, widget, *args):
        """emu title changed"""
        #get aletered text
        new_title = widget.get_text()
        #get combo box postion
        idx = self.cboEmu.get_active()
        #has title changed?
        if new_title != self.emu_lists[idx][0] and new_title != '':
            #update emulators combo box
            self.emu_lists[idx][0] = new_title
            mdl = self.cboEmu.get_model()
            mdl[idx][0] = new_title
            self.setup_altered = True

    def on_cboEmuLists_changed(self, *args):
        """emulator list combo"""
        if self.current_emu_list:
            #save emu list settings
            self.save_emulator_list_settings()
        #get settings for current emu list
        idx = self.cboEmuLists.get_active()
        self.current_emu_list = self.emu_game_lists[idx]
        if idx >= 0:
            self.load_emulator_list_settings(idx, self.current_emu_list[1])

    def on_txeEmuListTitle_changed(self, widget, *args):
        """list title changed"""
        #get aletered text
        new_title = widget.get_text()
        #get combo box postion
        idx = self.cboEmuLists.get_active()
        # Get IDX listed in combo box, support for non-sequential lists
        new_idx = self.cboEmuLists.get_model()[idx][0].split(':')[0]
        if new_idx != idx:
            idx = int(new_idx)
        #has title changed?
        if new_title != self.emu_game_lists[idx][0] and new_title != '':
            #update emulator lists combo box
            self.emu_game_lists[idx][0] = new_title
            mdl = self.cboEmuLists.get_model()
            mdl[idx][0] = '%s: %s' % (idx, new_title)
            self.setup_altered = True

    def on_btnWCOpenLayoutDir_clicked(self, widget, *args):
        """open layout dir"""
        self.open_dir_dialog(
            self.get_path(os.path.join(
                self.config_dir, 'layouts', self.txeWCLayoutDir.get_text())),
            'Set Layout Directory',
            self.set_layout_dir)

    def on_btnWCMovieIntroOpen_clicked(self, widget, *args):
        """intro movie file"""
        self.open_file_dialog(
            self.txeWCMovieIntro.get_text(),
            _('Set Intro Movie'),
            self.txeWCMovieIntro.set_text)

    def on_btnWCMovieExitOpen_clicked(self, widget, *args):
        """exit movie file"""
        self.open_file_dialog(
            self.txeWCMovieExit.get_text(),
            _('Set Exit Movie'),
            self.txeWCMovieExit.set_text)

    def on_btnWCOpenMusicDir_clicked(self, widget, *args):
        """open music dir"""
        self.open_dir_dialog(
            self.get_path(self.txeWCMusicDir.get_text()),
            'Set Music Directory',
            self.txeWCMusicDir.set_text)

    def on_btnEmuAdd_clicked(self, *args):
        """add new set of emulator files"""
        dlg = DlgAddEmu(SETUP_GLADE_FILE, 'dlgAddEmu', self)

    def on_btnEmuRemove_clicked(self, *args):
        """delete current set of emulator files"""
        #are you sure?
        dlg = gtk.MessageDialog(
            self.winSetup,
            gtk.DIALOG_MODAL,
            gtk.MESSAGE_QUESTION,
            gtk.BUTTONS_YES_NO,
            _('Are you sure you delete this Emulator (%s)?' % (self.current_emu[0])))
        resp = dlg.run()
        if resp == gtk.RESPONSE_YES:
            #go delete stuff
            emu_ini_name = self.current_emu[1]
            #remove emulator files (.fav, -nn.ftr, -nn.lst)
            self.remove_filespec('files', '%s.fav*' % emu_ini_name)
            self.remove_filespec('files', '%s-*.ftr' % emu_ini_name)
            self.remove_filespec('files', '%s-*.lst' % emu_ini_name)
            #remove ini files
            self.remove_filespec('ini', '%s-*.ini' % emu_ini_name)
            self.remove_filespec('ini', '%s.ini' % emu_ini_name)
            #reload settings
            self.load_settings()
            self.setup_altered = False
        dlg.destroy()

    def on_btnEmuListNew_clicked(self, *args):
        """add new emulator list files"""
        next_emu_list_num = len(self.cboEmuLists.get_model())
        emu_ini_name = self.current_emu[1]
        #copy template to ini dir
        shutil.copy2(
            os.path.join(APP_PATH, 'templates', 'default-1.ini'),
            os.path.join(self.config_dir, 'ini', '%s-%s.ini' % (emu_ini_name, next_emu_list_num)))
        #save & then reload
        self.save_emulator_list_settings()
        self.current_emu_list = None
        self.load_emulator_settings(self.current_emu[1], self.current_emu[2], next_emu_list_num)

    def on_btnEmuListDelete_clicked(self, *args):
        """delete current emulators list files"""
        #are you sure?
        dlg = gtk.MessageDialog(
            self.winSetup,
            gtk.DIALOG_MODAL,
            gtk.MESSAGE_QUESTION,
            gtk.BUTTONS_YES_NO,
            _('Are you sure you want to delete this List (%s)?' % (self.current_emu_list[0])))
        resp = dlg.run()
        if resp == gtk.RESPONSE_YES:
            #go delete stuff
            emu_ini_name = self.current_emu[1]
            emu_list_idx = self.cboEmuLists.get_active()
            self.remove_filespec('files', '%s-%s.ftr' % (emu_ini_name, emu_list_idx))
            self.remove_filespec('files', '%s-%s.lst' % (emu_ini_name, emu_list_idx))
            #remove ini files
            self.remove_filespec('ini', '%s-%s.ini' % (emu_ini_name, emu_list_idx))
            #renumber lists
            check_num = 1
            while check_num < MAX_LISTS:
                #find next missing file
                curr_ini = os.path.join(self.config_dir, 'ini', '%s-%s.ini' % (emu_ini_name, check_num))
                next_ini = os.path.join(self.config_dir, 'ini', '%s-%s.ini' % (emu_ini_name, (check_num + 1)))
                if not os.path.isfile(curr_ini) and  os.path.isfile(next_ini):
                    #rename next to current
                    os.rename(next_ini, curr_ini)
                    #rename list & filter files too
                    curr_ftr = os.path.join(self.config_dir, 'files', '%s-%s.ftr' % (emu_ini_name, check_num))
                    curr_lst = os.path.join(self.config_dir, 'files', '%s-%s.lst' % (emu_ini_name, check_num))
                    next_ftr = os.path.join(self.config_dir, 'files', '%s-%s.ftr' % (emu_ini_name, (check_num + 1)))
                    next_lst = os.path.join(self.config_dir, 'files', '%s-%s.lst' % (emu_ini_name, (check_num + 1)))
                    if os.path.isfile(curr_ftr):
                        os.remove(curr_ftr)
                    if os.path.isfile(curr_lst):
                        os.remove(curr_lst)
                    if os.path.isfile(next_ftr):
                        os.rename(next_ftr, curr_ftr)
                    if os.path.isfile(next_lst):
                        os.rename(next_lst, curr_lst)
                else:
                    #check next
                    check_num += 1
            #load emu list 0
            self.current_emu_list = 0
            self.load_emulator_settings(self.current_emu[1], self.current_emu[2])
        dlg.destroy()

    def on_btnEmuListFilter_clicked(self, *args):
        """set filter for list"""
        #idx = self.cboEmuLists.get_active()
        self.save_setups(False)
        self.WinFilter = WinFilter(SETUP_GLADE_FILE, 'winFilter', self.current_emu[1])#, idx)

    def on_btnEmuListEdit_clicked(self, *args):
        """edit the game list"""
        self.save_setups()
        self.WinList = WinList(
            SETUP_GLADE_FILE,
            'winList',
            self.current_emu[1],
            self.cboEmuLists.get_active())

    def on_btnEmuExeOpen_clicked(self, widget, *args):
        """emu executable"""
        self.open_file_dialog(
            self.get_path(self.txeEmuExe.get_text()),
            _('Set Emulator Executable'),
            self.txeEmuExe.set_text)

    def on_btnEmuRomDir_clicked(self, widget, *args):
        """emu rom dir"""
        self.open_dir_dialog(
            self.txeEmuRomDir.get_text(),
            _('Set Rom Directory'),
            self.txeEmuRomDir.set_text)

    def on_btnEmuNMSOpen_clicked(self, widget, *args):
        """nms file"""
        self.open_file_dialog(
            self.get_path(self.txeEmuNMSFile.get_text()),
            _('Set NMS File'),
            self.txeEmuNMSFile.set_text)

    def on_btnEmuScrMovieDir_clicked(self, widget, *args):
        """emu screen saver movie dir"""
        self.open_dir_dialog(
            self.txeEmuScrMovieDir.get_text(),
            _('Set Screen Saver Movie Directory'),
            self.txeEmuScrMovieDir.set_text)

    def on_btnEmuScrExternal_clicked(self, widget, *args):
        """emu external screen saver"""
        self.open_file_dialog(
            self.txeEmuScrExternal.get_text(),
            _('Set External Screen Saver'),
            self.txeEmuScrExternal.set_text)

    def on_btnEmuArt_clicked(self, widget, *args):
        """set emulator artwork dir"""
        idx = self.emu_artwork_btn.index(widget)
        self.open_dir_dialog(
            self.get_path(self.emu_artwork_txe[idx].get_text()),
            _('Set Artwork #%s Directory') % (idx + 1),
            self.emu_artwork_txe[idx].set_text)

    def on_btnEmuMovieDir_clicked(self, widget, *args):
        """emu movie dir"""
        self.open_dir_dialog(
            self.txeEmuMovieDir.get_text(),
            _('Set Movie Directory'),
            self.txeEmuMovieDir.set_text)

    def on_btnEmuExtApp_clicked(self, widget, *args):
        """set emu external app"""
        if widget == self.btnEmuExtApp1:
            txe = self.cboeEmuExtApp1.child
        elif widget == self.btnEmuExtApp2:
            txe = self.cboeEmuExtApp2.child
        else:
            txe = self.cboeEmuExtApp3.child
        self.open_file_dialog(
            self.get_path(self.txeMameXMLFile.get_text()),
            _('Set External Application'),
            txe.set_text)

    def on_btnMameXMLFile_clicked(self, widget, *args):
        """set mame xml info file"""
        self.open_file_dialog(
            self.get_path(self.txeMameXMLFile.get_text()),
            _('Set XML / Data File'),
            self.txeMameXMLFile.set_text)

    def on_btnMameCatver_clicked(self, widget, *args):
        """set mame xml catver.ini file"""
        self.open_file_dialog(
            self.get_path(self.txeMameCatver.get_text()),
            _('Set Category Version File'),
            self.txeMameCatver.set_text)

    def on_btnHstDatFile_clicked(self, widget, *args):
        """set history viewer history.dat file"""
        self.open_file_dialog(
            self.get_path(self.txeHstDatFile.get_text()),
            _('Set History Viewer history.dat File'),
            self.txeHstDatFile.set_text)

    def on_btnHstLayout_clicked(self, widget, *args):
        """set mame history viewer layout file"""
        self.open_file_dialog(
            self.get_path(self.txeHstLayout.get_text()),
            _('Set History Viewer Layout File'),
            self.txeHstLayout.set_text)

    def on_btnCPVIni_clicked(self, widget, *args):
        """set mame control panel viewer controls.ini file"""
        self.open_file_dialog(
            self.get_path(self.txeCPVIni.get_text()),
            _('Set Control Panel Viewer controls.ini File'),
            self.txeCPVIni.set_text)

    def on_btnCPVLayout_clicked(self, widget, *args):
        """set mame control panel viewer layout file"""
        self.open_file_dialog(
            self.get_path(self.txeCPVLayout.get_text()),
            _('Set Control Panel Viewer Layout File'),
            self.txeCPVLayout.set_text)

    def on_btnMameXMLGen_clicked(self, widget, *args):
        """generate mame xml info file"""
        #make sure mame emu is selected

        if self.current_emu[1] not in MAME_INI_FILES:
            self.show_msg_dialog(msg=_('Please select MAME/MESS Emulator first'))
            self.nbk.set_current_page(2)
            return
        #check mame exe exists
        if not os.path.isfile(self.txeEmuExe.get_text()):
            self.show_msg_dialog(msg=_('Please select valid MAME/MESS Application first'))
            self.nbk.set_current_page(2)
            return
        #default xml filename
        if self.txeMameXMLFile.get_text() == '' or not os.access(self.txeMameXMLFile.get_text(), os.W_OK):
            self.txeMameXMLFile.set_text(
                os.path.join(self.config_dir, 'files', 'mameinfo.xml'))
        #display wait dialog
        self.DlgWait = DlgWait(SETUP_GLADE_FILE, 'dlgWait', _('Please Wait. Creating XML File...'))
        #generate xml file
        if sys.platform != 'win32':
            redirect = ' 2>/dev/null'
        else:
            redirect = ''
        cmd = '%s -listxml > %s%s' % (
            self.txeEmuExe.get_text(),
            self.txeMameXMLFile.get_text(),
            redirect)
        #run emulator & wait for it to finish
        self.listxml_pid = Popen(cmd, shell=True)
        self.listxml_timer = gobject.timeout_add(500, self.wait_for_mame_listxml)

    def set_layout_dir(self, new_dir):
        """set layout directory"""
        self.txeWCLayoutDir.set_text(os.path.basename(new_dir))

    def wait_for_mame_listxml(self):
        """wait for listxml process to finish"""
        ret = self.listxml_pid.poll()
        if ret is not None:
            #finished - close wait dialog
            self.DlgWait.dlgWait.destroy()
            return False
        else:
            #still running...
            self.DlgWait.pgbWait.pulse()
            self.do_events()
            return True

    def save_setups(self, show_dialog=True):
        """save setup, prompt if show_dialog == True"""
        if self.setup_altered:
            ok_to_save = True
            if show_dialog:
                dlg = gtk.MessageDialog(
                    self.winSetup,
                    gtk.DIALOG_MODAL,
                    gtk.MESSAGE_QUESTION,
                    gtk.BUTTONS_YES_NO,
                    _('Save changes?'))
                resp = dlg.run()
                if resp != gtk.RESPONSE_YES:
                    ok_to_save = False
                dlg.destroy()
            #save?
            if ok_to_save:
                self.save_emulator_list_settings()
                self.save_emulator_settings()
                self.save_wahcade_settings()
                self.setup_altered = False

    def load_settings(self, default_emu=None):
        """load wahcade settings"""
        #build list of emulators
        self.emu_lists = self.buildemulist()
        self.current_emu = None
        self.current_emu_list = None
        #load emu combo
        l = ['%s (%s.ini)' % (e[0], e[1]) for e in self.emu_lists]
        self.setup_combo_box(self.cboEmu, l)
        #wahcade
        self.txeWCLayoutDir.set_text(self.wahcade_ini.get('layout'))
        self.chkWCFullscreen.set_active((self.wahcade_ini.getint('fullscreen', 0) == 1))
        self.spnWCScrDelay.set_value(self.wahcade_ini.getint('delay'))
        self.spnWCScrSlide.set_value(self.wahcade_ini.getint('slide_duration'))
        self.spnWCMovieDelay.set_value(self.wahcade_ini.getint('delay_before_movie_preview'))
        self.hscWCMovieVolume.set_value(self.wahcade_ini.getint('movie_volume'))
        ini_mix = self.wahcade_ini.get('music_movie_mix')
        mix_idx = [idx for idx, r in enumerate(self.music_movie_mix) if r[0] == ini_mix][0]
        self.cboWCMovieMix.set_active(mix_idx)
        self.txeWCMovieIntro.set_text(self.wahcade_ini.get('intro_movie_file'))
        self.txeWCMovieExit.set_text(self.wahcade_ini.get('exit_movie_file'))
        self.txeWCMusicDir.set_text(self.wahcade_ini.get('music_path'))
        self.chkWCMusic.set_active((self.wahcade_ini.getint('enable_music', 0) == 1))
        self.hscWCMusicVolume.set_value(self.wahcade_ini.getint('music_volume'))
        self.chkWCMusicShuffle.set_active((self.wahcade_ini.getint('shuffle_music', 0) == 1))
        self.chkWCMouseCursor.set_active((self.wahcade_ini.getint('show_cursor') == 1))
        self.chkWCWrapLists.set_active((self.wahcade_ini.getint('wrap_list') == 1))
        self.chkWCScaleImages.set_active((self.wahcade_ini.getint('keep_image_aspect') == 1))
        self.chkWCListArrows.set_active((self.wahcade_ini.getint('show_list_arrows', 0) == 1))
        #set emu
        set_idx = 0
        if default_emu:
            set_idx = [idx for idx, e in enumerate(self.emu_lists) if e[1] == default_emu][0]
        self.cboEmu.set_active(set_idx)
        #mame history viewer
        self.txeHstDatFile.set_text(self.histview_ini.get('history_dat_file'))
        self.txeHstLayout.set_text(self.histview_ini.get('history_layout'))
        #mame cp viewer
        self.txeCPVIni.set_text(self.cpviewer_ini.get('controls_ini_file'))
        self.txeCPVLayout.set_text(self.cpviewer_ini.get('viewer_layout'))
        #load keys
        self.chkKeysUseKeyboard.set_active((self.ctrlr_ini.getint('keyboard') == 1))
        self.chkKeysUseMouse.set_active((self.ctrlr_ini.getint('mouse') == 1))
        self.chkKeysUseJoystick.set_active((self.ctrlr_ini.getint('joystick') == 1))
        self.populate_keys()

    def load_emulator_settings(self, ini_name, emu_ini, default_list=0):
        """load emu settings"""
        
        # Default For Screens
        self.txeMameXMLFile.set_sensitive(True)
        self.btnMameXMLFile.set_sensitive(True)
        self.btnMameXMLGen.set_sensitive(True)
        self.btnEmuListFilter.set_sensitive(True)
        
        self.txeEmuTitle.set_text(emu_ini.get('emulator_title'))
        self.txeEmuExe.set_text(emu_ini.get('emulator_executable'))
        self.txeEmuCmdLine.set_text(emu_ini.get('commandline_format'))
        self.txeEmuAltCmdLine1.set_text(emu_ini.get('alt_commandline_format_1'))
        self.txeEmuAltCmdLine2.set_text(emu_ini.get('alt_commandline_format_2'))
        self.txeEmuRomExt.set_text(emu_ini.get('rom_extension'))
        self.txeEmuRomDir.set_text(emu_ini.get('rom_path'))
        self.txeEmuNMSFile.set_text(emu_ini.get('nms_file'))
        #list gen type
        ini_lgen = emu_ini.get('list_generation_method')
        try:
            lgen_idx = [idx for idx, r in enumerate(self.emu_list_gen_types) if ini_lgen in r[0]][0]
            self.cboEmuListGen.set_active(lgen_idx)
        except:
            print "Cannot load emulator settings, something went wrong!!"
        #artwork
        for idx, emu_art in enumerate(self.emu_artwork_txe):
            emu_art.set_text(emu_ini.get('artwork_%s_image_path' % (idx + 1)))
        self.txeEmuMovieDir.set_text(emu_ini.get('movie_preview_path'))
        self.spnEmuMovieNum.set_value(emu_ini.getint('movie_artwork_no'))
        self.cboeEmuExtApp1.child.set_text(emu_ini.get('app_1_executable'))
        self.txeEmuExtApp1.set_text(emu_ini.get('app_1_commandline_format'))
        self.cboeEmuExtApp2.child.set_text(emu_ini.get('app_2_executable'))
        self.txeEmuExtApp2.set_text(emu_ini.get('app_2_commandline_format'))
        self.cboeEmuExtApp3.child.set_text(emu_ini.get('app_3_executable'))
        self.txeEmuExtApp3.set_text(emu_ini.get('app_3_commandline_format'))
        self.txeEmuExtAuto.set_text(emu_ini.get('auto_launch_apps'))
        #screen saver
        ini_scr = emu_ini.get('saver_type')
        scr_idx = [idx for idx, r in enumerate(self.emu_scrsave_types) if r[0] == ini_scr][0]
        self.cboEmuScrSaver.set_active(scr_idx)
        self.txeEmuScrMovieDir.set_text(emu_ini.get('movie_path'))
        self.txeEmuScrExternal.set_text(emu_ini.get('scr_file'))
        #load lists
        self.emu_game_lists = []
        ini_files = self.build_filelist("", "ini", "(?<=-)\d+", ini_name, "-")
        for ini_file in ini_files:
            if os.path.isfile(ini_file):
                list_ini = MameWahIni(ini_file)
                ini_num = ini_file.split('-')
                self.emu_game_lists.append([list_ini.get('list_title'), list_ini, ini_num[1].split('.')[0]])
        l = ['%s: %s' % (r[2], r[0]) for i, r in enumerate(self.emu_game_lists)]
        self.setup_combo_box(self.cboEmuLists, l)
        self.cboEmuLists.set_active(default_list)

        self.txeMameXMLFile.set_text(emu_ini.get('dat_file'))
        self.txeMameCatver.set_text(emu_ini.get('catver_ini_file'))

        self.btnMameXMLGen.set_tooltip_text('Generate XML File')
        #mame only
        if not ini_name in MAME_INI_FILES:
            self.btnMameXMLGen.set_sensitive(False)
            self.btnMameXMLGen.set_tooltip_text('Not available for this emulator, Only available for known MAME/MESS derivatives')
        
        if emu_ini.get('catver_ini_file') == "":
            self.btnEmuListFilter.set_sensitive(False)

    def load_emulator_list_settings(self, emu_list_idx, emu_list_ini):
        """load emulator list"""
        self.txeEmuListTitle.set_text(emu_list_ini.get('list_title'))
        #default or user-def list
        if emu_list_idx >= 1:
            #user defined list
            list_type = emu_list_ini.get('list_type')
            type_idx = [i for i, r in enumerate(self.emu_list_types) if r[0] == list_type][0]
            print type_idx
            self.cboEmuListType.set_sensitive(True)
            self.btnEmuListDelete.set_sensitive(True)
        else:
            #default list
            type_idx = -1
            self.cboEmuListType.set_sensitive(False)
            self.btnEmuListDelete.set_sensitive(False)
        #set list type
        self.cboEmuListType.set_active(type_idx)
        self.chkEmuListCycle.set_active(emu_list_ini.getint('cycle_list') == 1)
        self.txeELCmdLine.set_text(emu_list_ini.get('commandline_format'))
        self.txeELAltCmdLine1.set_text(emu_list_ini.get('alt_commandline_format_1'))
        self.txeELAltCmdLine2.set_text(emu_list_ini.get('alt_commandline_format_2'))

    def save_wahcade_settings(self):
        """save wahcade settings"""
        #shift focus in order for spinner controls to update
        self.txeWCLayoutDir.grab_focus()
        #wahcade
        self.wahcade_ini.set('layout', self.txeWCLayoutDir.get_text())
        self.wahcade_ini.set('fullscreen', int(self.chkWCFullscreen.get_active()))
        self.wahcade_ini.set('delay', int(self.spnWCScrDelay.get_value()))
        self.wahcade_ini.set('slide_duration', int(self.spnWCScrSlide.get_value()))
        self.wahcade_ini.set('delay_before_movie_preview', int(self.spnWCMovieDelay.get_value()))
        self.wahcade_ini.set('movie_volume', int(self.hscWCMovieVolume.get_value()))
        self.wahcade_ini.set('music_movie_mix', self.music_movie_mix[self.cboWCMovieMix.get_active()][0])
        self.wahcade_ini.set('intro_movie_file', self.txeWCMovieIntro.get_text())
        self.wahcade_ini.set('exit_movie_file', self.txeWCMovieExit.get_text())
        self.wahcade_ini.set('music_path', self.txeWCMusicDir.get_text())
        self.wahcade_ini.set('enable_music', int(self.chkWCMusic.get_active()))
        self.wahcade_ini.set('music_volume', int(self.hscWCMusicVolume.get_value()))
        self.wahcade_ini.set('shuffle_music', int(self.chkWCMusicShuffle.get_active()))
        self.wahcade_ini.set('show_cursor', int(self.chkWCMouseCursor.get_active()))
        self.wahcade_ini.set('wrap_list', int(self.chkWCWrapLists.get_active()))
        self.wahcade_ini.set('keep_image_aspect', int(self.chkWCScaleImages.get_active()))
        self.wahcade_ini.set('show_list_arrows', int(self.chkWCListArrows.get_active()))
        #save ini
        self.wahcade_ini.write()
        #save controller settings
        #self.ctrlr_ini.set('keyboard', int(self.chkKeysUseKeyboard.get_active()))
        self.ctrlr_ini.set('mouse', int(self.chkKeysUseMouse.get_active()))
        self.ctrlr_ini.set('joystick', int(self.chkKeysUseJoystick.get_active()))
        self.ctrlr_ini.write()

    def save_emulator_settings(self):
        """save current emulator settings"""
        ini_name = self.current_emu[1]
        emu_ini = self.current_emu[2]
        emu_ini.set('emulator_title', self.txeEmuTitle.get_text())
        emu_ini.set('emulator_executable', self.txeEmuExe.get_text())
        emu_ini.set('commandline_format', self.txeEmuCmdLine.get_text())
        emu_ini.set('alt_commandline_format_1', self.txeEmuAltCmdLine1.get_text())
        emu_ini.set('alt_commandline_format_2', self.txeEmuAltCmdLine2.get_text())
        if self.txeEmuRomExt.get_text().startswith('.'):
            self.txeEmuRomExt.set_text(self.txeEmuRomExt.get_text()[1:])
        emu_ini.set('rom_extension', self.txeEmuRomExt.get_text())
        emu_ini.set('rom_path', self.txeEmuRomDir.get_text())
        emu_ini.set('nms_file', self.txeEmuNMSFile.get_text())
        emu_ini.set('list_generation_method', self.emu_list_gen_types[self.cboEmuListGen.get_active()][0][0])
        for idx, emu_art in enumerate(self.emu_artwork_txe):
            emu_ini.set('artwork_%s_image_path' % (idx + 1), emu_art.get_text())
        emu_ini.set('movie_preview_path', self.txeEmuMovieDir.get_text())
        emu_ini.set('movie_artwork_no', int(self.spnEmuMovieNum.get_value()))
        emu_ini.set('app_1_executable', self.cboeEmuExtApp1.child.get_text())
        emu_ini.set('app_1_commandline_format', self.txeEmuExtApp1.get_text())
        emu_ini.set('app_2_executable', self.cboeEmuExtApp2.child.get_text())
        emu_ini.set('app_2_commandline_format', self.txeEmuExtApp2.get_text())
        emu_ini.set('app_3_executable', self.cboeEmuExtApp3.child.get_text())
        emu_ini.set('app_3_commandline_format', self.txeEmuExtApp3.get_text())
        emu_ini.set('auto_launch_apps', self.txeEmuExtAuto.get_text())
        emu_ini.set('saver_type', self.emu_scrsave_types[self.cboEmuScrSaver.get_active()][0])
        emu_ini.set('movie_path', self.txeEmuScrMovieDir.get_text())
        emu_ini.set('scr_file', self.txeEmuScrExternal.get_text())
        emu_ini.set('catver_ini_file', self.txeMameCatver.get_text())
        #mame only
        if ini_name in MAME_INI_FILES:
            emu_ini.set('dat_file', self.txeMameXMLFile.get_text())
            #mame history viewer
            self.histview_ini.set('history_dat_file', self.txeHstDatFile.get_text())
            self.histview_ini.set('history_layout', self.txeHstLayout.get_text())
            #mame cp viewer
            self.cpviewer_ini.set('controls_ini_file', self.txeCPVIni.get_text())
            self.cpviewer_ini.set('viewer_layout', self.txeCPVLayout.get_text())
            #save
            self.histview_ini.write()
            self.cpviewer_ini.write()
        #save emu in ifiles
        emu_ini.write()

    def save_emulator_list_settings(self):
        """save emulator game list"""
        emu_list_ini = self.current_emu_list[1]
        emu_list_ini.set('list_title', self.txeEmuListTitle.get_text())
        if self.emu_game_lists.index(self.current_emu_list) >= 1:
            list_type = self.emu_list_types[self.cboEmuListType.get_active()][0]
            emu_list_ini.set('list_type', list_type)
        emu_list_ini.set('cycle_list', int(self.chkEmuListCycle.get_active()))
        emu_list_ini.set('commandline_format', self.txeELCmdLine.get_text())
        emu_list_ini.set('alt_commandline_format_1', self.txeELAltCmdLine1.get_text())
        emu_list_ini.set('alt_commandline_format_2', self.txeELAltCmdLine2.get_text())
        #save
        emu_list_ini.write()

    def create_new_emulator_files(self, template_ini_name, dest_ini_name):
        """create a new set of emulator files"""
        #copy template files to ini dir
        shutil.copy2(
            os.path.join(APP_PATH, 'templates', '%s.ini' % template_ini_name),
            os.path.join(self.config_dir, 'ini', '%s.ini' % dest_ini_name))
        shutil.copy2(
            os.path.join(APP_PATH, 'templates', 'default-0.ini'),
            os.path.join(self.config_dir, 'ini', '%s-0.ini' % dest_ini_name))
        #save & then reload
        self.on_mnuFSave_activate()
        self.load_settings(default_emu = dest_ini_name)

    def populate_keys(self):
        """pop keys list"""
        self.lsKeys.clear()
        #for each
        for ck, cv in self.ctrlr_ini.ini_dict.items():
            cv = str(cv)
            lv = cv.strip(' "').split(' | ')
            kb_vals = [v for v in lv if v.startswith('DIK_')]
            mouse_vals = [v for v in lv if v.startswith('MOUSE_')]
            joy_vals = [v for v in lv if v.startswith('JOY')]
            key_desc = ''
            #get key descriptions
            for keyval in kb_vals:
                keyname = [k for k, v in mamewah_keys.items() if keyval in v]
                if keyname != []:
                    if key_desc != '':
                        key_desc = '%s or %s' % (key_desc, keyname[0].upper())
                    else:
                        key_desc = '%s' % (keyname[0].upper())
            #get mouse descriptions
            for mouseval in mouse_vals:
                mousename = [k for k, v in _mouse_ctrls.items() if mouseval in v]
                if mousename != []:
                    if key_desc != '':
                        key_desc = '%s or %s' % (key_desc, mousename[0].upper())
                    else:
                        key_desc = '%s' % (mousename[0].upper())
            #get joystick descriptions
            for joyval in joy_vals:
                joyname = [k for k, v in self.joystick.ctrls.items() if joyval in v]
                if joyname != []:
                    if key_desc != '':
                        key_desc = '%s or %s' % (key_desc, joyname[0].upper())
                    else:
                        key_desc = '%s' % (joyname[0].upper())
            if ck.isupper():
                self.lsKeys.append((ck, key_desc))

    def open_file_dialog(self, default_filename, dlg_title, load_function):
        """open file dialog"""
        dlg = gtk.FileChooserDialog(
            title = dlg_title,
            action = gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        ftr = gtk.FileFilter()
        ftr.set_name("All files (*.*)")
        ftr.add_pattern("*")
        dlg.add_filter(ftr)
        dlg.set_filter(ftr)
        ftr = gtk.FileFilter()
        ftr.set_name("Config files (*.ini)")
        ftr.add_pattern("*.ini")
        dlg.add_filter(ftr)
        ftr = gtk.FileFilter()
        ftr.set_name("XML files (*.xml)")
        ftr.add_pattern("*.xml")
        dlg.add_filter(ftr)
        ftr = gtk.FileFilter()
        ftr.set_name("Dat files (*.dat)")
        ftr.add_pattern("*.dat")
        dlg.add_filter(ftr)
        if os.path.exists(default_filename):
            dlg.set_filename(default_filename)
        else:
            #dlg.set_current_folder(self.config_dir)
            dlg.set_current_folder(os.path.expanduser('~/'))
        response = dlg.run()
        if response == gtk.RESPONSE_OK:
            load_function(dlg.get_filename())
        dlg.destroy()

    def open_dir_dialog(self, default_dir, dlg_title, dlg_cb):
        """choose directory dialog"""
        dlg = gtk.FileChooserDialog(
            title = dlg_title,
            action = gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
            buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        if os.path.exists(default_dir):
            dlg.set_filename(default_dir)
        else:
            dlg.set_current_folder(os.path.expanduser('~/'))
        response = dlg.run()
        if response == gtk.RESPONSE_OK:
            dlg_cb(dlg.get_filename())
        dlg.destroy()

    def save_layout_dialog(self, default_filename, dlg_title, save_function):
        """save file as... dialog"""
        dlg = gtk.FileChooserDialog(
            title = dlg_title,
            action = gtk.FILE_CHOOSER_ACTION_SAVE,
            buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        ftr = gtk.FileFilter()
        ftr.set_name("All files")
        ftr.add_pattern("*")
        dlg.add_filter(ftr)
        ftr = gtk.FileFilter()
        ftr.set_name("Ini files")
        ftr.add_pattern("*.ini")
        dlg.add_filter(ftr)
        dlg.set_filter(ftr)
        if gtk.check_version(2, 8, 0) is None:
            try:
                dlg.set_do_overwrite_confirmation(True)
            except AttributeError:
                pass
        dlg.set_filename(default_filename)
        response = dlg.run()
        if response == gtk.RESPONSE_OK:
            save_function(dlg.get_filename())
        dlg.destroy()

    def remove_filespec(self, *filespec):
        """delete files with given filespec"""
        files = glob.glob(os.path.join(self.config_dir, *filespec))
        [os.remove(f) for f in files]

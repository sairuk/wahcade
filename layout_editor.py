#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
###
# Application: wah!cade
# File:        layout_editor.py
# Description: Wah!Cade Layout Editor
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
import shutil
import glob
#thanks to Trent Mick (http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/475126)
try:
    import xml.etree.cElementTree as ET # python >=2.5 C module
except ImportError:
    try:
        import xml.etree.ElementTree as ET # python >=2.5 pure Python module
    except ImportError:
        try:
            import cElementTree as ET # effbot's C module
        except ImportError:
            try:
                import elementtree.ElementTree as ET # effbot's pure Python module
            except ImportError:
                try:
                    import lxml.etree as ET # ElementTree API using libxml2
                except ImportError:
                    import warnings
                    warnings.warn("could not import ElementTree "
                                  "(http://effbot.org/zone/element-index.htm)")
#project imports
from constants import *
from glade2 import *
from wc_common import WahCade
from layout_props import DlgProps
from layout_scr_props import DlgScreenProps
from mamewah_ini import MameWahIni
_ = gettext.gettext


class WinLayout(GladeSupport, WahCade):
    """Layout Editor Main Window"""

    def __init__(self, glade_filename, window_name, config_opts, config_args):
        """build the window"""
        self.title = 'Wah!Cade Layout Editor'
        WahCade.__init__(self)
        GladeSupport.__init__(self, glade_filename, window_name)
        #dnd constants
        self.dnd_target_type_pixmap = 81
        self.dnd_evb = [('image/x-xpixmap', 0, self.dnd_target_type_pixmap)]
        #command-line options
        self.config_opts = config_opts
        if self.config_opts.use_app_config:
            #application config
            self.config_dir = os.path.join(APP_PATH, 'config')
        else:
            #got with the default config location
            self.config_dir = CONFIG_DIR
            if not os.path.exists(self.config_dir):
                sys.exit(_('No Wah!Cade config files found.  Run wahcade or wahcade-setup first.'))
        self.fixdMain = gtk.Fixed()
        self.fixdOpt = gtk.Fixed()
        self.fixdMsg = gtk.Fixed()
        self.fixdScr = gtk.Fixed()
        self.fixdCpv = gtk.Fixed()
        self.fixdHist = gtk.Fixed()
        self.fixd = self.fixdMain
        #background
        self.fixdBg = gtk.Fixed()
        self.fixdBg.show()
        self.imgBg = gtk.Image()
        self.imgBg.show()
        self.fixdBg.put(self.imgBg, 0, 0)
        #widgets
        self._main_widgets = [
            'Main Logo', 'Game List Indicator', 'Emulator Name', 'Game Selected',
            'Game Description', 'Rom Name', 'Year Manufacturer', 'Screen Type',
            'Controller Type', 'Driver Status', 'Cat Ver', 'Games List',
            'Artwork1', 'Artwork2', 'Artwork3', 'Artwork4', 'Artwork5',
            'Artwork6', 'Artwork7', 'Artwork8', 'Artwork9', 'Artwork10']
        self._opt_widgets = [
            'Heading', 'Options List', 'Setting Heading', 'Setting Value']
        self._msg_widgets = [
            'Heading', 'Message', 'Prompt']
        self._scr_widgets = [
            'Artwork1', 'Artwork2', 'Artwork3', 'Artwork4', 'Artwork5',
            'Artwork6', 'Artwork7', 'Artwork8', 'Artwork9', 'Artwork10',
            'Game Description', 'MP3 Name']
        self._cpv_widgets = [
            'P1JoyUp', 'P1JoyDown', 'P1JoyLeft', 'P1JoyRight',
            'P1B1', 'P1B2', 'P1B3', 'P1B4', 'P1B5', 'P1B6', 'P1B7', 'P1B8',
            'P2JoyUp', 'P2JoyDown', 'P2JoyLeft', 'P2JoyRight',
            'P2B1', 'P2B2', 'P2B3', 'P2B4', 'P2B5', 'P2B6', 'P2B7', 'P2B8',
            'P1JoyType', 'P2JoyType', 'GameName', 'NumPlayers', 'History',
            'Spinner1', 'Spinner2']
        self._hist_widgets = [
            'Heading', 'Game History']
        #labels
        main_widgets = {}
        opt_widgets = {}
        msg_widgets = {}
        scr_widgets = {}
        cpv_widgets = {}
        hist_widgets = {}
        for i, widget_name in enumerate(self._main_widgets):
            evb = self._make_label(widget_name)
            main_widgets[widget_name] = evb
            self.fixdMain.put(evb, 100, 10 + (i * 30))
        for i, widget_name in enumerate(self._opt_widgets):
            evb = self._make_label(widget_name)
            opt_widgets[widget_name] = evb
            self.fixdOpt.put(evb, 100, 10 + (i * 30))
        for i, widget_name in enumerate(self._msg_widgets):
            evb = self._make_label(widget_name)
            msg_widgets[widget_name] = evb
            self.fixdMsg.put(evb, 100, 10 + (i * 30))
        for i, widget_name in enumerate(self._scr_widgets):
            evb = self._make_label(widget_name)
            scr_widgets[widget_name] = evb
            self.fixdScr.put(evb, 100, 10 + (i * 30))
        for i, widget_name in enumerate(self._cpv_widgets):
            evb = self._make_label(widget_name)
            cpv_widgets[widget_name] = evb
            self.fixdCpv.put(evb, 0, 0)
        for i, widget_name in enumerate(self._hist_widgets):
            evb = self._make_label(widget_name)
            hist_widgets[widget_name] = evb
            self.fixdHist.put(evb, 100, 10 + (i * 30))
        #fixed pos widgets
        self._fixed_widgets = [self.fixdMain, self.fixdOpt, self.fixdMsg,
                self.fixdScr, self.fixdCpv, self.fixdHist]
        for fixd in self._fixed_widgets:
            fixd.connect('expose-event', self.on_fixd_expose_event)
            fixd.connect('drag-data-received', self.on_fixd_drag_data_received)
            fixd.connect('drag-motion', self.on_fixd_drag_motion)
            fixd.drag_dest_set(
                gtk.DEST_DEFAULT_MOTION | gtk.DEST_DEFAULT_HIGHLIGHT | gtk.DEST_DEFAULT_DROP,
                self.dnd_evb,
                gtk.gdk.ACTION_MOVE)
            fixd.show()
        #scrolled window viewport
        self.fixdBg.put(self.fixd, 0, 0)
        self.viewport = gtk.Viewport()
        self.scw.add(self.viewport)
        self.viewport.add(self.fixdBg)
        self.viewport.show()
        #setup main window
        self.winMain.add_events(gtk.gdk.KEY_PRESS)
        self.winMain.connect('key-press-event', self.on_winMain_key_press)
        self.winMain.connect('size-allocate', self.on_winMain_size_allocate)
        self.winMain.show()
        #properties dialogs
        self.dlg_props = DlgProps(LAYOUT_GLADE_FILE, 'dlgProps', self)
        self.dlg_props.populate_names(self._main_widgets)
        self.dlg_props.dlgProps.hide()
        self.dlg_screen = DlgScreenProps(LAYOUT_GLADE_FILE, 'dlgScreenProps', self)
        self.dlg_screen.dlgScreenProps.hide()
        #drag & drop stuff
        self.drag_cursor_move = gtk.gdk.Cursor(gtk.gdk.FLEUR)
        self.drag_cursor_resize = gtk.gdk.Cursor(gtk.gdk.BOTTOM_RIGHT_CORNER)
        self.selected_widgets = []
        self.drag_mode = ''
        self.drag_widget = None
        #layout stuff
        self.dLayout= {}
        self._layout_windows = [
            (1, self.fixdMain),
            (294, self.fixdOpt),
            (353, self.fixdMsg),
            (-1, self.fixdScr)]
        self._layout_items = [
            (8, main_widgets['Main Logo']),
            (21, main_widgets['Game List Indicator']),
            (34, main_widgets['Emulator Name']),
            (47, main_widgets['Games List']),
            (60, main_widgets['Game Selected']),
            (73, main_widgets['Artwork1']),
            (86, main_widgets['Artwork2']),
            (99, main_widgets['Artwork3']),
            (112, main_widgets['Artwork4']),
            (125, main_widgets['Artwork5']),
            (138, main_widgets['Artwork6']),
            (151, main_widgets['Artwork7']),
            (164, main_widgets['Artwork8']),
            (177, main_widgets['Artwork9']),
            (190, main_widgets['Artwork10']),
            (203, main_widgets['Game Description']),
            (216, main_widgets['Rom Name']),
            (229, main_widgets['Year Manufacturer']),
            (242, main_widgets['Screen Type']),
            (255, main_widgets['Controller Type']),
            (268, main_widgets['Driver Status']),
            (281, main_widgets['Cat Ver']),
            (301, opt_widgets['Heading']),
            (314, opt_widgets['Options List']),
            (327, opt_widgets['Setting Heading']),
            (340, opt_widgets['Setting Value']),
            (357, msg_widgets['Heading']),
            (370, msg_widgets['Message']),
            (383, msg_widgets['Prompt']),
            (396, scr_widgets['Artwork1']),
            (409, scr_widgets['Artwork2']),
            (422, scr_widgets['Artwork3']),
            (435, scr_widgets['Artwork4']),
            (448, scr_widgets['Artwork5']),
            (461, scr_widgets['Artwork6']),
            (474, scr_widgets['Artwork7']),
            (487, scr_widgets['Artwork8']),
            (500, scr_widgets['Artwork9']),
            (513, scr_widgets['Artwork10']),
            (526, scr_widgets['Game Description']),
            (539, scr_widgets['MP3 Name'])]
        self._histview_items = [
            (8, hist_widgets['Heading']),
            (21, hist_widgets['Game History'])]
        self.main_widgets = main_widgets
        self.opt_widgets = opt_widgets
        self.msg_widgets = msg_widgets
        self.scr_widgets = scr_widgets
        self.cpv_widgets = cpv_widgets
        self.hist_widgets = hist_widgets
        #setup view menu / toolbar
        self.view_updating = True
        self.view_menu = [self.mnuVMain, self.mnuVOpt, self.mnuVMsg, self.mnuVScr,
            self.mnuVCpv, self.mnuVHist]
        self.view_trb = [self.trbMain, self.trbOpt, self.trbMsg, self.trbScr,
            self.trbCpv, self.trbHist]
        for mnu in self.view_menu[1:]:
            mnu.set_active(False)
        #load layout
        self.layout_altered = False
        self.cpviewer_altered = False
        self.histview_altered = False
        if len(config_args) > 0:
            #load layout specified from command-line parameter
            self.load_layout_file(config_args[0])
            if len(config_args) > 1:
                #load cpviewer layout specified from command-line parameter
                self.load_cpviewer_file(config_args[1])
        else:
            #load default layouts
            wahcade_ini = MameWahIni(os.path.join(self.config_dir, 'wahcade.ini'), 'default')
            cpviewer_ini = MameWahIni(os.path.join(self.config_dir, 'cpviewer.ini'), 'default', '0.10')
            histview_ini = MameWahIni(os.path.join(self.config_dir, 'histview.ini'), 'default', '0.16')
            #setup layout combo
            self.layouts = []
            layout_files = glob.glob(os.path.join(self.config_dir, 'layouts', wahcade_ini.get('layout'), '*.lay'))
            for layout_file in layout_files:
                self.layouts.append(
                    [os.path.splitext(os.path.basename(layout_file))[0],
                    layout_file])
            self.layouts.sort()
            #setup layout combo
            l = ['%s.lay' % (l[0]) for l in self.layouts]
            self.setup_combo_box(self.cboLayout, l)
            #load layout
            layout_file = os.path.join(self.config_dir, 'layouts', wahcade_ini.get('layout'), 'layout.lay')
            if not os.path.isfile(layout_file):
                layout_file = os.path.join(self.config_dir, 'layouts', wahcade_ini.get('layout'), 'mame.lay')
                if not os.path.exists(layout_file):
                    try:
                        layout_file = layout_files[0]
                    except IndexError:
                        pass
                    if not os.path.exists(layout_file):
                        layout_file = os.path.join(self.config_dir, 'layouts', 'classic_640x480', 'layout.lay')
            idx = [self.layouts.index(l) for l in self.layouts if l[1] == layout_file]
            if idx != []:
                self.cboLayout.set_active(idx[0])
            else:
                self.load_layout_file(layout_file)
            self.cboLayout.set_sensitive(False)
            #load cpviewer
            cpviewer_file = self.get_path(cpviewer_ini.get('viewer_layout'))
            if not os.path.isfile(cpviewer_file):
                cpviewer_file = os.path.join(self.config_dir, 'layouts', 'classic_cpviewer', 'example.lay')
            self.load_cpviewer_file(cpviewer_file)
            #load history viewer
            histview_file = self.get_path(histview_ini.get('history_layout'))
            if not os.path.isfile(histview_file):
                histview_file = os.path.join(self.config_dir, 'layouts', 'classic_histview', 'example.lay')
            self.load_histview_file(histview_file)
        #display main window layout
        self.view_updating = False
        self.mnuVMain.set_active(True)
        self.on_rbWindow_toggled(self.mnuVMain)

    def on_winMain_delete_event(self, *args):
        """done, quit the application"""
        if self.layout_altered or self.cpviewer_altered or self.histview_altered:
            msg = _('Save:')
            if self.layout_altered:
                msg += _('\n  Wah!Cade Layout')
            if self.cpviewer_altered:
                msg += _('\n  CPViewer Layout')
            if self.histview_altered:
                msg += _('\n  History Viewer Layout')
            dlg = gtk.MessageDialog(
                self.winMain,
                gtk.DIALOG_MODAL,
                gtk.MESSAGE_QUESTION,
                gtk.BUTTONS_YES_NO,
                msg)
            resp = dlg.run()
            if resp == gtk.RESPONSE_YES:
                if self.layout_altered:
                    self.save_layout_file()
                if self.cpviewer_altered:
                    self.save_cpviewer_file()
                if self.histview_altered:
                    self.save_histview_file()
            dlg.destroy()
        #exit gtk loop
        gtk.main_quit()
        return False

    def on_winMain_key_press(self, widget, event, *args):
        """key pressed - move selected widget"""
        if self.selected_widgets == []:
            return
        if event.type == gtk.gdk.KEY_PRESS:
            #keyboard pressed, get gtk keyname
            keyname = gtk.gdk.keyval_name(event.keyval).lower()
            shift_key = event.state & gtk.gdk.SHIFT_MASK
            #widget
            for sel_widget in self.selected_widgets:
                dx = 0
                dy = 0
                #which key pressed
                if keyname == 'up':
                    dy = -1
                elif keyname == 'down':
                    dy = +1
                elif keyname == 'left':
                    dx = -1
                elif keyname == 'right':
                    dx = +1
                else:
                    return
                #shift pressed?
                if shift_key:
                    #update size
                    self.dLayout[sel_widget]['width'] += dx
                    self.dLayout[sel_widget]['height'] += dy
                    sel_widget.set_size_request(self.dLayout[sel_widget]['width'], self.dLayout[sel_widget]['height'])
                else:
                    #update positon
                    self.dLayout[sel_widget]['x'] += dx
                    self.dLayout[sel_widget]['y'] += dy
                    self.fixd.move(sel_widget, self.dLayout[sel_widget]['x'], self.dLayout[sel_widget]['y'])
                #set properties
                self.dlg_props.set_properties(sel_widget, self.dLayout[sel_widget])
                self.set_layout_altered(sel_widget)

    def on_winMain_size_allocate(self, widget, allocation):
        """main window size has changed"""
        #re-allocate all fixed container widgets
        for fixd in self._fixed_widgets:
            fixd.set_size_request(allocation.width, allocation.height)
            #fixd.size_allocate(allocation)

    def on_mnuFOpen_activate(self, *args):
        """open wahcade layout"""
        self.open_layout_dialog(
            self.layout_filename,
            _('Open Wah!Cade Layout'),
            self.load_layout_file)
        self.set_window_title()

    def on_mnuFOpenCPV_activate(self, *args):
        """open cpviewer layout"""
        self.open_layout_dialog(
            self.cpviewer_filename,
            _('Open CP Viewer Layout'),
            self.load_cpviewer_file)
        self.set_window_title()

    def on_mnuFOpenHist_activate(self, *args):
        """open histview layout"""
        self.open_layout_dialog(
            self.histview_filename,
            _('Open History Viewer Layout'),
            self.load_histview_file)
        self.set_window_title()

    def on_mnuFSave_activate(self, *args):
        """save"""
        if self.layout_altered:
            self.save_layout_file()
        if self.cpviewer_altered:
            self.save_cpviewer_file()
        if self.histview_altered:
            self.save_histview_file()

    def on_mnuFSaveAs_activate(self, *args):
        """save wahcade layout file as"""
        self.save_layout_dialog(
            self.layout_filename,
            _('Save Wah!Cade Layout'),
            self.save_layout_file)
        self.set_window_title()

    def on_mnuFSaveCPVAs_activate(self, *args):
        """save cpviewer layout file as"""
        self.save_layout_dialog(
            self.cpviewer_filename,
            _('Save CP Viewer Layout'),
            self.save_cpviewer_file)
        self.set_window_title()

    def on_mnuFSaveHistAs_activate(self, *args):
        """save history viewer layout file as"""
        self.save_layout_dialog(
            self.histview_filename,
            _('Save History Viewer Layout'),
            self.save_histview_file)
        self.set_window_title()

    def on_mnuFQuit_activate(self, *args):
        """quit"""
        self.on_winMain_delete_event()

    def on_mnuESelectAllVisible_activate(self, *args):
        """select all visible widgets"""
        for widget in self.fixd.get_children():
            if self.dLayout[widget]['visible']:
                self.select_widget(widget)
                self.selected_widgets.append(widget)

    def on_mnuESelectAll_activate(self, *args):
        """select all widgets"""
        for widget in self.fixd.get_children():
            self.select_widget(widget)
            self.selected_widgets.append(widget)

    def on_cboLayout_changed(self, cbo, *args):
        """change layout"""
        self.load_layout_file(self.layouts[cbo.get_active()][1])

    def on_rbWindow_toggled(self, widget, *args):
        """change window"""
        #print "on_rbWindow_toggled: ",widget.get_name(), widget.get_active()
        if self.view_updating:
            return
        if widget not in self.view_menu:
            self.view_updating = True
            for mnu in self.view_menu:
                mnu.set_active(False)
        if widget not in self.view_trb:
            self.view_updating = True
            for trb in self.view_trb:
                trb.set_active(False)
        if widget.get_active():
            self.fixdBg.remove(self.fixd)
            if widget in [self.trbMain, self.mnuVMain]:
                #main
                self.mnuVMain.set_active(True)
                self.trbMain.set_active(True)
                self.fixd = self.fixdMain
                self.dlg_props.populate_names(self._main_widgets)
            elif widget in [self.trbOpt, self.mnuVOpt]:
                #options
                self.mnuVOpt.set_active(True)
                self.trbOpt.set_active(True)
                self.fixd = self.fixdOpt
                self.dlg_props.populate_names(self._opt_widgets)
            elif widget in [self.trbMsg, self.mnuVMsg]:
                #message
                self.mnuVMsg.set_active(True)
                self.trbMsg.set_active(True)
                self.fixd = self.fixdMsg
                self.dlg_props.populate_names(self._msg_widgets)
            elif widget in [self.trbScr, self.mnuVScr]:
                #screen saver
                self.mnuVScr.set_active(True)
                self.trbScr.set_active(True)
                self.fixd = self.fixdScr
                self.dlg_props.populate_names(self._scr_widgets)
            elif widget in [self.trbCpv, self.mnuVCpv]:
                #c.p. viewer
                self.mnuVCpv.set_active(True)
                self.trbCpv.set_active(True)
                self.fixd = self.fixdCpv
                self.dlg_props.populate_names(self._cpv_widgets)
            elif widget in [self.trbHist, self.mnuVHist]:
                #history viewer
                self.mnuVHist.set_active(True)
                self.trbHist.set_active(True)
                self.fixd = self.fixdHist
                self.dlg_props.populate_names(self._hist_widgets)
            #set background colour
            self.viewport.modify_bg(
                gtk.STATE_NORMAL,
                gtk.gdk.color_parse(self.dLayout[self.fixd]['background-col']))
            #set background image
            image_filename = self.get_path(self.dLayout[self.fixd]['image'])
            if not os.path.dirname(image_filename):
                if self.fixd == self.fixdCpv:
                    img_path = os.path.dirname(self.cpviewer_filename)
                elif self.fixd == self.fixdHist:
                    img_path = os.path.dirname(self.histview_filename)
                else:
                    img_path = os.path.dirname(self.layout_filename)
                image_filename = os.path.join(img_path, image_filename)
            if os.path.isfile(image_filename):
                self.imgBg.set_from_file(image_filename)
                self.imgBg.set_property('visible', True)
            else:
                #self.imgBg.clear()
                self.imgBg.set_from_file(None)
                self.imgBg.set_property('visible', False)
            #show correct view
            self.fixdBg.put(self.fixd, 0, 0)
            self.dlg_screen.set_properties()
            #set window title
            self.set_window_title()
        self.view_updating = False

    def on_mnuVItemProps_activate(self, *args):
        """show item properties dialog"""
        self.dlg_props.dlgProps.present()

    def on_mnuVScreenProps_activate(self, *args):
        """show screen properties dialog"""
        self.dlg_screen.dlgScreenProps.present()

    def on_mnuVOnTop_toggled(self, widget, *args):
        """toggle property windows on top / not on top"""
        self.dlg_props.dlgProps.set_keep_above(widget.get_active())
        self.dlg_screen.dlgScreenProps.set_keep_above(widget.get_active())

    def on_mnuVFullScreen_toggled(self, widget, *args):
        """toggle fullscreen mode"""
        if self.mnuVFullScreen.get_active():
            self.winMain.fullscreen()
        else:
            self.winMain.unfullscreen()

    def on_mnuHAbout_activate(self, *args):
        """about dialog"""
        self.show_about_dialog(self.title, self.config_dir)

    def on_evb_pressed(self, widget, event, *args):
        """mouse button down"""
        #set widgets
        self.drag_widget = widget
        if event.button == 1:
            #actually select the widget
            self.select_widget(self.drag_widget)
            #set mode
            w, h = self.drag_widget.get_size_request()
            if event.x >= (w - 8) and event.y >= (h - 8):
                self.drag_mode = 'resize'
            else:
                self.drag_mode = 'move'
            if event.button == 1 and (event.state & gtk.gdk.CONTROL_MASK):
                #multiple widgets
                self.selected_widgets.append(self.drag_widget)
            else:
                #one widget
                self.deselect_widgets(leave_selected=self.drag_widget)
            #set properties
            self.dlg_props.set_properties(self.drag_widget, self.dLayout[self.drag_widget])
            #self.do_events()
        elif event.button == 3:
            self.select_widget(self.drag_widget)
            self.dlg_props.set_properties(self.drag_widget, self.dLayout[self.drag_widget])
            self.on_mnuVItemProps_activate()
            self.deselect_widgets(leave_selected=self.drag_widget)

    def on_evb_drag_begin(self, widget, context):
        """drag & drop starting"""
        #set relevant drag icon
        if self.drag_mode == 'resize':
            self.drag_widget.drag_source_set_icon_stock(gtk.STOCK_DND)
        elif self.drag_mode == 'move':
            #set drag & drop icon (use widget as a pixbuf)
            self.do_events()
            width, height = widget.window.get_size()
            pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, 0, 8, width, height)
            pixbuf.get_from_drawable(
                widget.window,
                widget.window.get_colormap(),
                0, 0, 0, 0,
                width, height)
            self.drag_widget.drag_source_set_icon_pixbuf(pixbuf)

    def on_evb_drag_data_get(self, widget, context, selection, target_type, event_time):
        """drag & drop start"""
        if target_type == self.dnd_target_type_pixmap:
            #set drag & drop data
            selection.set(selection.target, 8, widget.get_name())

    def on_fixd_drag_motion(self, widget, drag_context, x, y, timestamp):
        """drag & drop in progress"""
        if self.drag_mode == 'resize':
            #resize the dragged widget
            self.drag_widget.set_size_request(
                x - self.dLayout[self.drag_widget]['x'],
                y - self.dLayout[self.drag_widget]['y'])
        #ok to drop
        return True

    def on_fixd_drag_data_received(self, widget, context, x, y, selection, target_type, time):
        """drag & drop done"""
        if target_type == self.dnd_target_type_pixmap:
            if self.drag_mode == 'resize':
                #resize the widget
                self.drag_widget.set_size_request(
                    x - self.dLayout[self.drag_widget]['x'],
                    y - self.dLayout[self.drag_widget]['y'])
                self.dLayout[self.drag_widget]['width'] = x - self.dLayout[self.drag_widget]['x']
                self.dLayout[self.drag_widget]['height'] = y - self.dLayout[self.drag_widget]['y']
            else:
                #move the widget
                self.fixd.move(self.drag_widget, x, y)
                self.dLayout[self.drag_widget]['x'] = x
                self.dLayout[self.drag_widget]['y'] = y
            #re-select moved / resized widget
            self.drag_widget.window.raise_()
            self.select_widget(self.drag_widget)
            #set props
            self.dlg_props.set_properties(self.drag_widget, self.dLayout[self.drag_widget])
            self.set_layout_altered(self.drag_widget)

    def on_evb_expose_event(self, evb, event):
        """redraw eventbox around label"""
        #redraw selection & size boxes if widget is currently selected
        if evb == self.drag_widget:
            #get widget size
            w, h = evb.get_size_request()
            #draw outline
            evb.style.paint_focus(
                evb.window,
                gtk.STATE_SELECTED,
                None,
                evb,
                '1',
                0, 0,
                w, h)
            #draw resize rectangle
            evb.window.draw_rectangle(
                evb.style.black_gc,
                True,
                w - 6, h - 6,
                5, 5)
            #done - no further processing
            #return False
        #done
        return False

    def on_fixd_expose_event(self, fixed, event):
        """draw a border"""
        window = fixed.window
        w = self.dLayout[fixed]['width']
        h = self.dLayout[fixed]['height']
        gc = fixed.style.light_gc[gtk.STATE_NORMAL]
        window.draw_rectangle(gc, False, 0, 0, w, h)
        return False

    def _make_label(self, widget_name):
        """create a label (inside an event box)"""
        evb = gtk.EventBox()
        evb.set_name(widget_name)
        lbl = gtk.Label(widget_name)
        lbl.show()
        evb.set_size_request(100, 25)
        evb.set_visible_window(True)
        evb.show()
        evb.add(lbl)
        evb.connect('button-press-event', self.on_evb_pressed)
        evb.connect('drag-begin', self.on_evb_drag_begin)
        evb.connect('drag-data-get', self.on_evb_drag_data_get)
        evb.connect_after('expose-event', self.on_evb_expose_event)
        evb.drag_source_set(gtk.gdk.BUTTON1_MASK, self.dnd_evb, gtk.gdk.ACTION_MOVE)
        evb.set_property('visible', False)
        return evb

    def open_layout_dialog(self, default_filename, dlg_title, load_function):
        """open wahcade / cpviewer layout file dialog"""
        dlg = gtk.FileChooserDialog(
            title = dlg_title,
            action = gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        ftr = gtk.FileFilter()
        ftr.set_name('All files')
        ftr.add_pattern('*')
        dlg.add_filter(ftr)
        ftr = gtk.FileFilter()
        ftr.set_name('Layout files')
        ftr.add_pattern('*.lay')
        dlg.add_filter(ftr)
        dlg.set_filter(ftr)
        if os.path.exists(default_filename):
            dlg.set_filename(default_filename)
        else:
            dlg.set_current_folder(self.config_dir)
        response = dlg.run()
        if response == gtk.RESPONSE_OK:
            load_function(dlg.get_filename())
        dlg.destroy()

    def save_layout_dialog(self, default_filename, dlg_title, save_function):
        """save wahcade / cpviewer layout file as... dialog"""
        dlg = gtk.FileChooserDialog(
            title = dlg_title,
            action = gtk.FILE_CHOOSER_ACTION_SAVE,
            buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE_AS, gtk.RESPONSE_OK))
        ftr = gtk.FileFilter()
        ftr.set_name('All files')
        ftr.add_pattern('*')
        dlg.add_filter(ftr)
        ftr = gtk.FileFilter()
        ftr.set_name('Layout files')
        ftr.add_pattern('*.lay')
        dlg.add_filter(ftr)
        dlg.set_filter(ftr)
        if gtk.check_version(2, 8, 0) is None:
            try:
                dlg.set_do_overwrite_confirmation(True)
            except AttributeError:
                pass
        if os.path.exists(default_filename):
            dlg.set_filename(default_filename)
        else:
            dlg.set_current_folder(self.config_dir)
        response = dlg.run()
        if response == gtk.RESPONSE_OK:
            save_function(dlg.get_filename())
        dlg.destroy()

    def select_widget(self, widget):
        """widget selected"""
        #show widget as selected
        self.drag_widget = widget
        widget.set_property('visible', True)
        widget.set_state(gtk.STATE_SELECTED)
        widget.window.raise_()

    def deselect_widgets(self, leave_selected):
        """de-select all currently selected widgets"""
        for widget in self.selected_widgets:
            if widget != leave_selected:
                widget.set_state(gtk.STATE_NORMAL)
                if not self.dLayout[widget]['visible']:
                    #hide deselected widget invisble again
                    widget.set_property('visible', False)
        if leave_selected:
            self.selected_widgets = [leave_selected]
        else:
            self.selected_widgets = []

    def set_layout_altered(self, widget):
        """update layout altered flags"""
        if widget.get_name() in self.cpv_widgets or widget == self.fixdCpv:
            self.cpviewer_altered = True
        elif widget.get_name() in self.hist_widgets or widget == self.fixdHist:
            self.histview_altered = True
        else:
            self.layout_altered = True

    def load_layout_file(self, layout_filename):
        """load layout file"""
        self.layout_filename = layout_filename
        layout_path = os.path.dirname(layout_filename)
        #read file & strip any crap
        lines = open(layout_filename, 'r').readlines()
        lines = [s.strip() for s in lines]
        lines.insert(0, '.')
        #window sizes
        main_width, main_height = int(lines[1].split(';')[0]), int(lines[2])
        opt_width, opt_height = int(lines[294].split(';')[0]), int(lines[295])
        msg_width, msg_height = int(lines[353].split(';')[0]), int(lines[354])
        self.dLayout[self.fixdMain] = {
            'name': 'Main',
            'width': main_width, 'height': main_height}
        self.dLayout[self.fixdOpt] = {
            'name': 'Options',
            'width': opt_width, 'height': opt_height}
        self.dLayout[self.fixdMsg] = {
            'name': 'Message',
            'width': msg_width, 'height': msg_height}
        self.dLayout[self.fixdScr] = {
            'name': 'Screen Saver',
            'width': main_width, 'height': main_height}
        #main window
        if gtk.gdk.screen_width() > main_width and gtk.gdk.screen_height() > main_height:
            #set default size if screen size is big enough
            self.viewport.set_size_request(main_width, main_height)
            self.winMain.set_size_request(main_width, main_height)
        else:
            #minimum size
            self.viewport.set_size_request(640, 480)
            self.winMain.set_size_request(640, 480)
        self.dLayout[self.fixdMain]['background-col'] = self.get_colour(int(lines[3]))
        main_bg_col = gtk.gdk.color_parse(self.get_colour(int(lines[3])))
        self.viewport.modify_bg(gtk.STATE_NORMAL, main_bg_col)
        self.dLayout[self.fixdMain]['image'] = lines[4]
        img_file = self.get_path(lines[4])
        if not os.path.dirname(img_file):
            img_file = os.path.join(layout_path, img_file)
        #print "img=",img_file, os.path.isfile(img_file)
        self.dLayout[self.fixdMain]['use_image'] = os.path.isfile(img_file)
        #options window
        self.dLayout[self.fixdOpt]['background-col'] = self.get_colour(int(lines[296]))
        opt_bg_col = gtk.gdk.color_parse(self.get_colour(int(lines[296])))
        self.dLayout[self.fixdOpt]['image'] = lines[297]
        img_file = self.get_path(lines[297])
        if not os.path.dirname(img_file):
            img_file = os.path.join(layout_path, img_file)
        self.dLayout[self.fixdOpt]['use_image'] = os.path.isfile(img_file)
        #message window
        self.dLayout[self.fixdMsg]['background-col'] = self.get_colour(int(lines[355]))
        msg_bg_col = gtk.gdk.color_parse(self.get_colour(int(lines[355])))
        self.dLayout[self.fixdMsg]['image'] = lines[356]
        img_file = self.get_path(lines[356])
        if not os.path.dirname(img_file):
            img_file = os.path.join(layout_path, img_file)
        self.dLayout[self.fixdMsg]['use_image'] = os.path.isfile(img_file)
        #screen saver window
        self.dLayout[self.fixdScr]['background-col'] = self.dLayout[self.fixdMain]['background-col']
        self.dLayout[self.fixdScr]['image'] = ''
        self.dLayout[self.fixdScr]['use_image'] = False
        #set all window items
        for offset, widget in self._layout_items:
            #get properties
            d = self.get_layout_item_properties(lines, offset)
            self.dLayout[widget] = d
            #font
            fd = d['font']
            if d['font-bold']:
                fd += ' Bold'
            if d['font-italic']:
                fd += ' Italic'
            fd += ' %s' % (d['font-size'])
            d['font-name'] = fd
            font_desc = pango.FontDescription(fd)
            #list widget?
            if widget.get_name() == 'Games List':
                d['bar-col'] = self.get_colour(int(lines[6]))
                d['selected-col'] = self.get_colour(int(lines[7]))
            elif widget.get_name() == 'Options List':
                d['bar-col'] = self.get_colour(int(lines[299]))
                d['selected-col'] = self.get_colour(int(lines[300]))
            #label colours
            fg_col = gtk.gdk.color_parse(d['text-col'])
            bg_col = gtk.gdk.color_parse(d['background-col'])
            widget.child.modify_font(font_desc)
            widget.child.modify_fg(gtk.STATE_NORMAL, fg_col)
            if not d['transparent']:
                widget.modify_bg(gtk.STATE_NORMAL, bg_col)
            #alignment
            if d['text-align'] == 2:
                widget.child.set_property('xalign', 0.5)
            else:
                widget.child.set_property('xalign', d['text-align'])
            #rotation
            widget.child.set_angle(d['text-rotation'])
            #visible?
            widget.set_property('visible', d['visible'])
            #size
            widget.set_size_request(d['width'], d['height'])
            #move to fixed layout on correct window
            if offset < 293:
                #main window
                if d['transparent']:
                    widget.modify_bg(gtk.STATE_NORMAL, main_bg_col)
                self.fixdMain.move(widget, d['x'], d['y'])
            elif offset < 353:
                #options window
                if d['transparent']:
                    widget.modify_bg(gtk.STATE_NORMAL, opt_bg_col)
                self.fixdOpt.move(widget, d['x'], d['y'])
            elif offset < 396:
                #message window
                if d['transparent']:
                    widget.modify_bg(gtk.STATE_NORMAL, msg_bg_col)
                self.fixdMsg.move(widget, d['x'], d['y'])
            else:
                #screen saver window
                if d['transparent']:
                    widget.modify_bg(gtk.STATE_NORMAL, main_bg_col)
                self.fixdScr.move(widget, d['x'], d['y'])
        #finish up
        self.dlg_screen.set_properties()
        self.layout_altered = False
        #set to main window
        self.on_rbWindow_toggled(self.mnuVMain)

    def save_layout_file(self, layout_filename=None):
        """save layout"""
        if layout_filename:
            self.layout_filename = layout_filename
        #setup empty layout
        lines = [''] * 552
        #window widgets
        for offset, widget in self._layout_windows:
            if offset < 0:
                break
            d = self.dLayout[widget]
            lines[offset] = ' %s' % d['width']
            lines[offset + 1] = ' %s' % d['height']
            lines[offset + 2] = ' %s' % self.reverse_get_colour(d['background-col'])
            if d['use_image']:
                img_path = self.get_path(d['image'])
                if os.path.dirname(img_path) == os.path.dirname(self.layout_filename):
                    d['image'] = os.path.basename(img_path)
                lines[offset + 3] = ' %s' % d['image']
            else:
                lines[offset + 3] = ' '
            lines[offset + 4] = ' 1'
        #item widgets
        for offset, widget in self._layout_items:
            d = self.dLayout[widget]
            lines[offset] = str(d['visible'])
            lines[offset + 1] = ' %s' % int(d['transparent'])
            lines[offset + 2] = ' %s' % self.reverse_get_colour(d['background-col'])
            lines[offset + 3] = ' %s' % self.reverse_get_colour(d['text-col'])
            lines[offset + 4] = d['font']
            lines[offset + 5] = str(d['font-bold'])
            lines[offset + 6] = str(d['font-italic'])
            lines[offset + 7] = ' %s' % d['font-size']
            align_rot = '%s' % d['text-align']
            if d['text-rotation'] != 0:
                align_rot = '%s;%s' % (align_rot, d['text-rotation'])
            lines[offset + 8] = ' %s' % align_rot
            lines[offset + 9] = ' %s' % d['x']
            lines[offset + 10] = ' %s' % d['y']
            lines[offset + 11] = ' %s' % d['width']
            lines[offset + 12] = ' %s' % d['height']
            #extra list properties
            if widget.get_name() == 'Games List':
                lines[6] = ' %s' % self.reverse_get_colour(d['bar-col'])
                lines[7] = ' %s' % self.reverse_get_colour(d['selected-col'])
            elif widget.get_name() == 'Options List':
                lines[299] = ' %s' % self.reverse_get_colour(d['bar-col'])
                lines[300] = ' %s' % self.reverse_get_colour(d['selected-col'])
        #write file
        lines = ['%s\n' % (l) for l in lines]
        fname = os.path.join(self.layout_filename)
        open(fname, 'w').writelines(lines[1:])
        #reset altered flag
        self.layout_altered = False

    def init_cpviewer_widgets(self):
        """set cpviewer widgets to sensible defaults"""
        for widget in self._cpv_widgets:
            d = {}
            d['font'] = 'Sans'
            d['font-name'] = 'Sans 10'
            d['font-bold'] = False
            d['font-italic'] = False
            d['font-size'] = 10
            d['transparent'] = True
            d['text-col'] = '#FF0000'
            d['background-col'] = '#FFFFFF'
            d['visible'] = False
            d['text-align'] = 2
            d['width'] = 100
            d['height'] = 20
            d['x'] = 0
            d['y'] = 0
            #save widget settings
            evb = self.cpv_widgets[widget]
            self.dLayout[evb] = d

    def load_cpviewer_file(self, cpviewer_file):
        """load cpviewer layout"""
        #init all widgets first
        self.init_cpviewer_widgets()
        #load...
        self.cpviewer_filename = cpviewer_file
        if not os.path.isfile(cpviewer_file):
            print 'Error: control panel layout file: [%s] does not exist.' % (cpviewer_file)
            return
        cpv_width = 0
        cpv_height = 0
        cpv_img = ''
        for event, ctrl_element in ET.iterparse(cpviewer_file):
            if ctrl_element.tag in self._cpv_widgets:
                #d = {}
                evb = self.cpv_widgets[ctrl_element.tag]
                lbl = evb.child
                d = self.dLayout[evb]
                #font
                d['font'] = ctrl_element.find('FontName').text
                d['font-bold'] = (ctrl_element.find('FontBold').text == 'True')
                d['font-italic'] = (ctrl_element.find('FontItalic').text == 'True')
                d['font-size'] = int(ctrl_element.find('FontSize').text)
                if ctrl_element.find('Transparent') is not None:
                    d['transparent'] = (ctrl_element.find('Transparent').text == 'True')
                fd = d['font']
                if d['font-bold']:
                    fd += ' Bold'
                if d['font-italic']:
                    fd += ' Italic'
                fd += ' %s' % (d['font-size'])
                d['font-name'] = fd
                font_desc = pango.FontDescription(fd)
                #colours
                d['text-col'] = self.get_colour(abs(int(ctrl_element.find('ForeColor').text)))
                fg_col = gtk.gdk.color_parse(d['text-col'])
                lbl.modify_font(font_desc)
                lbl.modify_fg(gtk.STATE_NORMAL, fg_col)
                d['background-col'] = self.get_colour(abs(int(ctrl_element.find('BackColor').text)))
                bg_col = gtk.gdk.color_parse(d['background-col'])
                if not d['transparent']:
                    evb.modify_bg(gtk.STATE_NORMAL, bg_col)
                #visible?
                d['visible'] = (ctrl_element.find('Visible').text == 'True')
                evb.set_property('visible', d['visible'])
                #alignment
                if ctrl_element.find('TextAlign').text == 'MiddleLeft':
                    align = 0.0
                    text_align = 0
                elif ctrl_element.find('TextAlign').text == 'MiddleCenter':
                    align = 0.5
                    text_align = 2
                elif ctrl_element.find('TextAlign').text == 'MiddleRight':
                    align = 1.0
                    text_align = 1
                d['text-align'] = text_align
                lbl.set_alignment(align, 0.5)
                #rotation
                d['text-rotation'] = 0
                if ctrl_element.find('TextRotation') is not None:
                    d['text-rotation'] = int(ctrl_element.find('TextRotation').text)
                lbl.set_angle(d['text-rotation'])
                #move & size
                d['width'] = int(ctrl_element.find('Width').text)
                d['height'] = int(ctrl_element.find('Height').text)
                d['x'] = int(ctrl_element.find('Left').text)
                d['y'] = int(ctrl_element.find('Top').text)
                evb.set_size_request(d['width'], d['height'])
                self.fixdCpv.move(evb, d['x'], d['y'])
                #save widget settings
                self.dLayout[evb] = d
            elif ctrl_element.tag == 'MainForm':
                #setup background, etc
                cpv_width = int(ctrl_element.find('Width').text)
                cpv_height = int(ctrl_element.find('Height').text)
                cpv_img = ctrl_element.find('BGImage').text
                if not os.path.dirname(cpv_img):
                    cpv_img = os.path.join(os.path.dirname(self.cpviewer_filename), cpv_img)
                if ctrl_element.find('BackColor') is not None:
                    back_col = self.get_colour(abs(int(ctrl_element.find('BackColor').text)))
                else:
                    back_col = '#000000' #default background colour
                self.fixdCpv.set_size_request(cpv_width, cpv_height)
        self.dLayout[self.fixdCpv] = {
            'name': 'C.P. Viewer',
            'width': cpv_width, 'height': cpv_height,
            'background-col': back_col,
            'image': cpv_img,
            'use_image': os.path.isfile(self.get_path(cpv_img))}
        #done
        ctrl_element.clear()
        self.dlg_screen.set_properties()
        self.cpviewer_altered = False
        #set to main window
        self.on_rbWindow_toggled(self.mnuVCpv)

    def indent_cpviewer_file(self, elem, level=0):
        """correctly indent the cpviewer xml file"""
        i = "\n" + level*"  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            for e in elem:
                self.indent_cpviewer_file(e, level+1)
            if not e.tail or not e.tail.strip():
                e.tail = i
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

    def save_cpviewer_file(self, cpviewer_filename=None):
        """save the cpviewer layout file"""
        xml_elements = {
            'x': 'Left',
            'y': 'Top',
            'width': 'Width',
            'height': 'Height',
            'visible': 'Visible',
            'font': 'FontName',
            'font-size': 'FontSize',
            'font-bold': 'FontBold',
            'font-italic': 'FontItalic',
            'text-col': 'ForeColor',
            'background-col': 'BackColor',
            'text-align': 'TextAlign',
            'text-rotation': 'TextRotation',
            'transparent': 'Transparent'}
        #set filename
        if cpviewer_filename:
            self.cpviewer_filename = cpviewer_filename
        #create root xml node
        cpv_ele = ET.Element("CPViewer")
        #
        for cpv_widget in self._cpv_widgets:
            widget_ele = ET.SubElement(cpv_ele, cpv_widget)
            for k, v in self.dLayout[self.cpv_widgets[cpv_widget]].items():
                if k in xml_elements:
                    sub_ele = ET.SubElement(widget_ele, xml_elements[k])
                    if k in ['text-col', 'background-col']:
                        sub_ele.text = str(self.reverse_get_colour(v))
                    elif k == 'text-align':
                        if v == 0:
                            sub_ele.text = 'MiddleLeft'
                        elif v == 2:
                            sub_ele.text = 'MiddleCenter'
                        else:
                            sub_ele.text = 'MiddleRight'
                    else:
                        sub_ele.text = str(v)
        #main form
        mf_ele = ET.SubElement(cpv_ele, 'MainForm')
        d = self.dLayout[self.fixdCpv]
        ET.SubElement(mf_ele, 'Width').text = str(d['width'])
        ET.SubElement(mf_ele, 'Height').text = str(d['height'])
        if d['use_image']:
            img_path = self.get_path(d['image'])
            if os.path.dirname(img_path) == os.path.dirname(self.histview_filename):
                d['image'] = os.path.basename(img_path)
            ET.SubElement(mf_ele, 'BGImage').text = d['image']
        else:
            ET.SubElement(mf_ele, 'BGImage').text = ''
        ET.SubElement(mf_ele, 'BackColor').text = str(self.reverse_get_colour(d['background-col']))
        # wrap it in an ElementTree instance, and save as XML
        tree = ET.ElementTree(cpv_ele)
        #ident it properly
        self.indent_cpviewer_file(cpv_ele)
        tree.write(self.cpviewer_filename)
        #reset altered flag
        self.cpviewer_altered = False

    def load_histview_file(self, histview_filename):
        """load history viewer layout file"""
        #read file & strip any crap
        self.histview_filename = histview_filename
        if not os.path.isfile(histview_filename):
            print 'Error: history layout file: [%s] does not exist.' % (histview_filename)
            return
        lines = open(histview_filename, 'r').readlines()
        lines = [s.strip() for s in lines]
        lines.insert(0, '.')
        #window properties
        hist_width, hist_height = int(lines[1].split(';')[0]), int(lines[2])
        hist_bg_col = gtk.gdk.color_parse(self.get_colour(int(lines[3])))
        self.dLayout[self.fixdHist] = {
            'name': 'History',
            'width': hist_width, 'height': hist_height,
            'background-col': self.get_colour(int(lines[3]))}
        #background image
        self.dLayout[self.fixdHist]['image'] = lines[4]
        img_path = self.get_path(lines[4])
        if not os.path.dirname(img_path):
            img_path = os.path.join(os.path.dirname(self.histview_filename), img_path)
        self.dLayout[self.fixdHist]['use_image'] = os.path.isfile(img_path)
        #set window size
        self.fixdHist.set_size_request(hist_width, hist_height)
        #set all window items
        for offset, widget in self._histview_items:
            #get properties
            d = self.get_layout_item_properties(lines, offset)
            self.dLayout[widget] = d
            #font
            fd = d['font']
            if d['font-bold']:
                fd += ' Bold'
            if d['font-italic']:
                fd += ' Italic'
            fd += ' %s' % (d['font-size'])
            d['font-name'] = fd
            font_desc = pango.FontDescription(fd)
            #list widget?
            if widget.get_name() == 'Game History':
                d['bar-col'] = self.get_colour(int(lines[6]))
                d['selected-col'] = self.get_colour(int(lines[7]))
            #label colours
            fg_col = gtk.gdk.color_parse(d['text-col'])
            bg_col = gtk.gdk.color_parse(d['background-col'])
            widget.child.modify_font(font_desc)
            widget.child.modify_fg(gtk.STATE_NORMAL, fg_col)
            if d['transparent']:
                widget.modify_bg(gtk.STATE_NORMAL, hist_bg_col)
            else:
                widget.modify_bg(gtk.STATE_NORMAL, bg_col)
            #alignment
            if d['text-align'] == 2:
                widget.child.set_property('xalign', 0.5)
            else:
                widget.child.set_property('xalign', d['text-align'])
            #rotation
            widget.child.set_angle(d['text-rotation'])
            #visible?
            widget.set_property('visible', d['visible'])
            #size
            widget.set_size_request(d['width'], d['height'])
            #move on fixed layout
            self.fixdHist.move(widget, d['x'], d['y'])
        #finish up
        self.histview_altered = False

    def save_histview_file(self, histview_filename=None):
        """save history viewer layout file"""
        if histview_filename:
            self.histview_filename = histview_filename
        #setup empty layout
        lines = [''] * 34
        #window widget
        d = self.dLayout[self.fixdHist]
        lines[1] = ' %s' % d['width']
        lines[2] = ' %s' % d['height']
        lines[3] = ' %s' % self.reverse_get_colour(d['background-col'])
        if d['use_image']:
            img_path = self.get_path(d['image'])
            if os.path.dirname(img_path) == os.path.dirname(self.histview_filename):
                d['image'] = os.path.basename(img_path)
            lines[4] = ' %s' % d['image']
        else:
            lines[4] = ' '
        lines[5] = ' 1'
        #item widgets
        for offset, widget in self._histview_items:
            d = self.dLayout[widget]
            lines[offset] = str(d['visible'])
            lines[offset + 1] = ' %s' % int(d['transparent'])
            lines[offset + 2] = ' %s' % self.reverse_get_colour(d['background-col'])
            lines[offset + 3] = ' %s' % self.reverse_get_colour(d['text-col'])
            lines[offset + 4] = d['font']
            lines[offset + 5] = str(d['font-bold'])
            lines[offset + 6] = str(d['font-italic'])
            lines[offset + 7] = ' %s' % d['font-size']
            align_rot = '%s' % d['text-align']
            if d['text-rotation'] != 0:
                align_rot = '%s;%s' % (align_rot, d['text-rotation'])
            lines[offset + 8] = ' %s' % align_rot
            lines[offset + 9] = ' %s' % d['x']
            lines[offset + 10] = ' %s' % d['y']
            lines[offset + 11] = ' %s' % d['width']
            lines[offset + 12] = ' %s' % d['height']
            #extra list properties
            if widget.get_name() == 'Game History':
                lines[6] = ' %s' % self.reverse_get_colour(d['bar-col'])
                lines[7] = ' %s' % self.reverse_get_colour(d['selected-col'])
        #write file
        lines = ['%s\n' % (l) for l in lines]
        fname = os.path.join(self.histview_filename)
        open(fname, 'w').writelines(lines[1:])
        #reset altered flag
        self.histview_altered = False

    def set_window_title(self):
        """set window title"""
        if self.fixd == self.fixdCpv:
            self.winMain.set_title('%s - %s' % (self.title, self.cpviewer_filename))
        elif self.fixd == self.fixdHist:
            self.winMain.set_title('%s - %s' % (self.title, self.histview_filename))
        else:
            self.winMain.set_title('%s -%s' % (self.title, self.layout_filename))

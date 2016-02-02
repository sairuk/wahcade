#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
###
# Application: wah!cade
# File:        layout_props.py
# Description: Wah!Cade Layout Properties Dialog
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


class DlgProps(GladeSupport):
    """Layout Editor Item Properties Dialog"""

    def __init__(self, glade_filename, window_name, app):
        """build the window"""
        GladeSupport.__init__(self, glade_filename, window_name)
        #init
        self.WinLayout = app
        self.widget_list = []
        self.name_idx = -1
        self.updating = False

    def populate_names(self, widget_list):
        #pop names
        self.widget_list = widget_list
        self.setup_combo_box(self.cboName, widget_list)

    def on_dlgProps_delete_event(self, *args):
        """just hide window, not destroy it"""
        self.dlgProps.hide()
        return True

    def on_btnClose_clicked(self, *args):
        """hide properties dialog"""
        self.dlgProps.hide()

    def on_cboName_changed(self, *args):
        """name combo changed"""
        if not self.updating:
            if self.cboName.get_active() != self.name_idx:
                #get widget from correct window
                widget_name = self.cboName.get_active_text()
                if self.WinLayout.fixd == self.WinLayout.fixdMain:
                    widget = self.WinLayout.main_widgets[widget_name]
                elif self.WinLayout.fixd == self.WinLayout.fixdOpt:
                    widget = self.WinLayout.opt_widgets[widget_name]
                elif self.WinLayout.fixd == self.WinLayout.fixdMsg:
                    widget = self.WinLayout.msg_widgets[widget_name]
                elif self.WinLayout.fixd == self.WinLayout.fixdScr:
                    widget = self.WinLayout.scr_widgets[widget_name]
                elif self.WinLayout.fixd == self.WinLayout.fixdCpv:
                    widget = self.WinLayout.cpv_widgets[widget_name]
                elif self.WinLayout.fixd == self.WinLayout.fixdHist:
                    widget = self.WinLayout.hist_widgets[widget_name]
                #select it
                self.WinLayout.select_widget(widget)
                self.WinLayout.deselect_widgets(leave_selected=widget)
                self.set_properties(widget, self.WinLayout.dLayout[widget])

    def on_chkVisible_toggled(self, *args):
        """set widget visiblity"""
        if not self.updating:
            for widget in self.WinLayout.selected_widgets:
                self.WinLayout.dLayout[widget]['visible'] = self.chkVisible.get_active()
                widget.set_property('visible', self.chkVisible.get_active())
                self.WinLayout.set_layout_altered(widget)

    def on_chkTransparent_toggled(self, *args):
        """set widget transparency"""
        if not self.updating:
            for widget in self.WinLayout.selected_widgets:
                self.WinLayout.dLayout[widget]['transparent'] = self.chkTransparent.get_active()
                if self.chkTransparent.get_active():
                    clr = self.WinLayout.dLayout[self.WinLayout.fixd]['background-col']
                else:
                    clr = self.WinLayout.dLayout[widget]['background-col']
                widget.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse(clr))
                self.WinLayout.set_layout_altered(widget)

    def on_spnX_changed(self, *args):
        """change widget X pos"""
        if not self.updating:
            x = self.spnX.get_value_as_int()
            for widget in self.WinLayout.selected_widgets:
                self.WinLayout.dLayout[widget]['x'] = x
                self.WinLayout.fixd.move(widget, x, self.WinLayout.dLayout[widget]['y'])
                self.WinLayout.set_layout_altered(widget)

    def on_spnY_changed(self, *args):
        """change widget Y pos"""
        if not self.updating:
            y = self.spnY.get_value_as_int()
            for widget in self.WinLayout.selected_widgets:
                self.WinLayout.dLayout[widget]['y'] = y
                self.WinLayout.fixd.move(widget, self.WinLayout.dLayout[widget]['x'], y)
                self.WinLayout.set_layout_altered(widget)

    def on_spnWidth_changed(self, *args):
        """change widget width"""
        if not self.updating:
            w = self.spnWidth.get_value_as_int()
            for widget in self.WinLayout.selected_widgets:
                self.WinLayout.dLayout[widget]['width'] = w
                widget.set_size_request(w, self.WinLayout.dLayout[widget]['height'])
                self.WinLayout.set_layout_altered(widget)

    def on_spnHeight_changed(self, *args):
        """change widget height"""
        if not self.updating:
            h = self.spnHeight.get_value_as_int()
            for widget in self.WinLayout.selected_widgets:
                self.WinLayout.dLayout[widget]['height'] = h
                widget.set_size_request(self.WinLayout.dLayout[widget]['width'], h)
                self.WinLayout.set_layout_altered(widget)

    def on_clrText_color_set(self, widget, *args):
        """set text colour"""
        if not self.updating:
            clr, hex_clr = self.WinLayout.get_colorbutton_info(widget)
            for widget in self.WinLayout.selected_widgets:
                self.WinLayout.dLayout[widget]['text-col'] = hex_clr
                widget.child.modify_fg(gtk.STATE_NORMAL, clr)
                self.WinLayout.set_layout_altered(widget)

    def on_clrBar_color_set(self, widget, *args):
        """set list highlighted bar colour"""
        if not self.updating:
            clr, hex_clr = self.WinLayout.get_colorbutton_info(widget)
            for widget in self.WinLayout.selected_widgets:
                self.WinLayout.dLayout[widget]['bar-col'] = hex_clr
                self.WinLayout.set_layout_altered(widget)

    def on_clrSelected_color_set(self, widget, *args):
        """set list highlighted item colour"""
        if not self.updating:
            clr, hex_clr = self.WinLayout.get_colorbutton_info(widget)
            for widget in self.WinLayout.selected_widgets:
                self.WinLayout.dLayout[widget]['selected-col'] = hex_clr
                self.WinLayout.set_layout_altered(widget)

    def on_clrBackground_color_set(self, widget, *args):
        """set item background colour"""
        if not self.updating:
            clr, hex_clr = self.WinLayout.get_colorbutton_info(widget)
            for widget in self.WinLayout.selected_widgets:
                self.WinLayout.dLayout[widget]['background-col'] = hex_clr
                if not self.WinLayout.dLayout[widget]['transparent']:
                    widget.modify_bg(gtk.STATE_NORMAL, clr)
                self.WinLayout.set_layout_altered(widget)

    def on_rbTextAlign_toggled(self, rb, *args):
        """alignment changed"""
        if not self.updating:
            if rb.get_active():
                if rb == self.rbTextAlignL:
                    text_align = 0
                    xalign = 0.0
                elif rb == self.rbTextAlignC:
                    text_align = 2
                    xalign = 0.5
                elif rb == self.rbTextAlignR:
                    text_align = 1
                    xalign = 1.0
                for widget in self.WinLayout.selected_widgets:
                    self.WinLayout.dLayout[widget]['text-align'] = text_align
                    widget.child.set_property('xalign', xalign)
                    self.WinLayout.set_layout_altered(widget)

    def on_spnRotation_changed(self, cbo, *args):
        """text / image rotation"""
        if not self.updating:
            text_rot = self.spnRotation.get_value_as_int()
            for widget in self.WinLayout.selected_widgets:
                self.WinLayout.dLayout[widget]['text-rotation'] = text_rot
                widget.child.set_angle(text_rot)
                self.WinLayout.set_layout_altered(widget)

    def on_fontText_font_set(self, fnt, *args):
        """font changed"""
        if not self.updating:
            pfd = pango.FontDescription(fnt.get_font_name())
            for widget in self.WinLayout.selected_widgets:
                self.WinLayout.dLayout[widget]['font-name'] = fnt.get_font_name()
                self.WinLayout.dLayout[widget]['font'] = pfd.get_family()
                self.WinLayout.dLayout[widget]['font-bold'] = (pfd.get_weight() >= pango.WEIGHT_BOLD)
                self.WinLayout.dLayout[widget]['font-italic'] = (pfd.get_style() == pango.STYLE_ITALIC)
                self.WinLayout.dLayout[widget]['font-size'] = int(pfd.get_size() / pango.SCALE)
                widget.child.modify_font(pfd)
                self.WinLayout.set_layout_altered(widget)

    def on_btnArtworkDir_clicked(self, *args):
        """select artwork dir dialog"""
        pass

    def on_txeArtworkDir_changed(self, *args):
        """set artwork dir"""
        pass

    def on_chkPlaysMovies_toggled(self, *args):
        """play movies"""
        pass

    def on_btnMovieDir_clicked(self, *args):
        """select movie dir dialog"""
        pass

    def on_txeMovieDir_changed(self, *args):
        """set movie dir"""
        pass

    def set_properties(self, widget, widget_props):
        """set props for given widget"""
        self.name_idx = self.widget_list.index(widget.get_name())
        #set updating flag to stop events from processing
        self.updating = True
        #set props
        self.cboName.set_active(self.name_idx)
        self.chkVisible.set_active(widget_props['visible'])
        self.chkTransparent.set_active(widget_props['transparent'])
        self.spnX.set_value(widget_props['x'])
        self.spnY.set_value(widget_props['y'])
        self.spnWidth.set_value(widget_props['width'])
        self.spnHeight.set_value(widget_props['height'])
        self.fontText.set_font_name(widget_props['font-name'])
        self.clrBackground.set_color(gtk.gdk.color_parse(widget_props['background-col']))
        self.clrText.set_color(gtk.gdk.color_parse(widget_props['text-col']))
        if widget_props['text-align'] == 0:
            self.rbTextAlignL.set_active(True)
        elif widget_props['text-align'] == 1:
            self.rbTextAlignR.set_active(True)
        elif widget_props['text-align'] == 2:
            self.rbTextAlignC.set_active(True)
        self.spnRotation.set_value(widget_props['text-rotation'])
        #list widget?
        if widget.get_name() in ['Games List', 'Options List', 'Game History']:
            self.lblBar.set_sensitive(True)
            self.clrBar.set_sensitive(True)
            self.lblSelected.set_sensitive(True)
            self.clrSelected.set_sensitive(True)
            self.clrBar.set_color(gtk.gdk.color_parse(widget_props['bar-col']))
            self.clrSelected.set_color(gtk.gdk.color_parse(widget_props['selected-col']))
        else:
            self.lblBar.set_sensitive(False)
            self.clrBar.set_sensitive(False)
            self.lblSelected.set_sensitive(False)
            self.clrSelected.set_sensitive(False)
        self.updating = False

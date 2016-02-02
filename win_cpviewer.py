# -*- coding: utf-8 -*-
#
###
# Application: wah!cade
# File:        win_cpviewer.py
# Description: cp viewer window
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
#import new
#import types
import ConfigParser
try:
    import xml.etree.ElementTree as ET # in python >=2.5
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

#constants
_items = [
    'P1JoyUp', 'P1JoyDown', 'P1JoyLeft', 'P1JoyRight',
    'P1B1', 'P1B2', 'P1B3', 'P1B4', 'P1B5', 'P1B6', 'P1B7', 'P1B8',
    'P2JoyUp', 'P2JoyDown', 'P2JoyLeft', 'P2JoyRight',
    'P2B1', 'P2B2', 'P2B3', 'P2B4', 'P2B5', 'P2B6', 'P2B7', 'P2B8',
    'P1JoyType', 'P2JoyType', 'GameName', 'NumPlayers', 'History',
    'Spinner1', 'Spinner2']
_ctrls_map = {
    'P1JoyUp': ['P1_JOYSTICK_UP', 'P1_JOYSTICKLEFT_UP'],
    'P1JoyDown': ['P1_JOYSTICK_DOWN', 'P1_JOYSTICKLEFT_DOWN'],
    'P1JoyLeft': ['P1_JOYSTICK_LEFT', 'P1_JOYSTICKLEFT_LEFT'],
    'P1JoyRight': ['P1_JOYSTICK_RIGHT', 'P1_JOYSTICKLEFT_RIGHT'],
    'P1B1': ['P1_BUTTON1'],
    'P1B2': ['P1_BUTTON2'],
    'P1B3': ['P1_BUTTON3'],
    'P1B4': ['P1_BUTTON4'],
    'P1B5': ['P1_BUTTON5'],
    'P1B6': ['P1_BUTTON6'],
    'P1B7': ['P1_BUTTON7'],
    'P1B8': ['P1_BUTTON8'],
    'P2JoyUp': ['P2_JOYSTICK_UP', 'P1_JOYSTICKRIGHT_UP'],
    'P2JoyDown': ['P2_JOYSTICK_DOWN', 'P1_JOYSTICKRIGHT_DOWN'],
    'P2JoyLeft': ['P2_JOYSTICK_LEFT', 'P1_JOYSTICKRIGHT_LEFT'],
    'P2JoyRight': ['P2_JOYSTICK_RIGHT', 'P1_JOYSTICKRIGHT_RIGHT'],
    'P2B1': ['P2_BUTTON1'],
    'P2B2': ['P2_BUTTON2'],
    'P2B3': ['P2_BUTTON3'],
    'P2B4': ['P2_BUTTON4'],
    'P2B5': ['P2_BUTTON5'],
    'P2B6': ['P2_BUTTON6'],
    'P2B7': ['P2_BUTTON7'],
    'P2B8': ['P2_BUTTON8'],
    'P1JoyType': ['P1Controls'],
    'P2JoyType': ['P2Controls'],
    'GameName': ['gamename'],
    'NumPlayers': ['numPlayers'],
    'History': ['miscDetails'],
    'Spinner1': ['P1_PADDLE', 'P1_PADDLE_EXT'],
    'Spinner2': ['P1_PADDLE_V', 'P1_PADDLE_V_EXT']}


class WinCPViewer(WahCade):
    """cpviewer based control panel viewer"""

    def __init__(self, WinMain):
        """setup cp viewer window"""
        #set main window
        self.WinMain = WinMain
        self.layout_filename = ''
        self.cpviewer_ok = True
        #open cpviewer viewer ini
        self.cpviewer_ini = MameWahIni(os.path.join(CONFIG_DIR, 'cpviewer.ini'), 'default')
        if os.path.exists(os.path.join(CONFIG_DIR, 'ini', self.WinMain.current_emu + '.cpv')):
            self.cpviewer_ini = MameWahIni(os.path.join(CONFIG_DIR, 'ini', self.WinMain.current_emu + '.cpv'), 'default')
        self.ctrls_ini_filename = self.cpviewer_ini.get('controls_ini_file')
        if not os.path.isfile(self.ctrls_ini_filename):
            self.WinMain.log_msg("Warning: controls file: [%s] does not exist" % (self.ctrls_ini_filename))
            self.cpviewer_ok = False
        self.layout_filename = self.cpviewer_ini.get('viewer_layout')
        if not os.path.exists(self.layout_filename):
            self.WinMain.log_msg("Warning: CPViewer layout file: [%s] does not exist" % (self.layout_filename))
            self.cpviewer_ok = False
        #build gui
        self.winCPViewer = gtk.Fixed()
        self.winCPViewer.set_has_window(True)
        self.imgBackground = gtk.Image()
        self.winCPViewer.add(self.imgBackground)
        self.WinMain.fixd.add(self.winCPViewer)
        self.imgBackground.show()
        self.winCPViewer.show()
        self.ctrls_ini = self.get_controls_ini(self.ctrls_ini_filename)
        if self.ctrls_ini is None:
            self.cpviewer_ok = False
        self.app_number = 0

    def on_winMain_delete_event(self, *args):
        """exit window"""
        #hide window
        self.WinMain.hide_window('cpviewer')
        return True

    def _make_label(self, widget_name):
        """create a label (inside an event box)"""
        evb = gtk.EventBox()
        evb.set_name(widget_name)
        lbl = gtk.Label(widget_name)
        lbl.show()
        #lbl.set_line_wrap(True)
        lbl.set_text('')
        evb.set_size_request(100, 25)
        evb.set_visible_window(True)
        evb.show()
        evb.add(lbl)
        evb.set_property('visible', False)
        return evb

    def load_layout(self, xml_filename):
        """parse cpviewer xml file and create & position labels"""
        if not os.path.isfile(xml_filename):
            return
        #init widgets
        cpv_widgets = {}
        for i, widget_name in enumerate(_items):
            evb = self._make_label(widget_name)
            cpv_widgets[widget_name] = evb
            self.winCPViewer.add(evb)
        #get category info
        for event, ctrl_element in ET.iterparse(xml_filename):
            if ctrl_element.tag in _items:
                #get label / event box
                evb = cpv_widgets[ctrl_element.tag]
                lbl = evb.child
                #font
                fd = ctrl_element.find('FontName').text
                if ctrl_element.find('FontBold').text == 'True':
                    fd += ' Bold'
                if ctrl_element.find('FontItalic').text == 'True':
                    fd += ' Italic'
                fd += ' %s' % (ctrl_element.find("FontSize").text)
                font_desc = pango.FontDescription(fd)
                #colours
                transparent = True
                if ctrl_element.find('Transparent') is not None:
                    transparent = (ctrl_element.find('Transparent').text == 'True')
                fg_col = gtk.gdk.color_parse(self.get_colour(abs(int(ctrl_element.find('ForeColor').text))))
                bg_col = gtk.gdk.color_parse(self.get_colour(abs(int(ctrl_element.find('BackColor').text))))
                lbl.modify_font(font_desc)
                lbl.modify_fg(gtk.STATE_NORMAL, fg_col)
                if transparent:
                    evb.set_visible_window(False)
                else:
                    evb.modify_bg(gtk.STATE_NORMAL, bg_col)
                #visible?
                evb.set_property('visible', ctrl_element.find('Visible').text == 'True')
                #alignment
                if ctrl_element.find('TextAlign').text == 'MiddleLeft':
                    align = 0.0
                    justify = gtk.JUSTIFY_LEFT
                elif ctrl_element.find('TextAlign').text == 'MiddleCenter':
                    align = 0.5
                    justify = gtk.JUSTIFY_CENTER
                elif ctrl_element.find('TextAlign').text == 'MiddleRight':
                    align = 1.0
                    justify = gtk.JUSTIFY_RIGHT
                lbl.set_alignment(align, 0.5)
                lbl.set_property('justify', justify)
                #rotation
                text_rot = 0
                if ctrl_element.find('TextRotation') is not None:
                    text_rot = int(ctrl_element.find('TextRotation').text)
                lbl.set_angle(text_rot)
                #move & size
                evb.set_size_request(
                    int(ctrl_element.find('Width').text),
                    int(ctrl_element.find('Height').text))
                self.winCPViewer.move(
                    evb,
                    int(ctrl_element.find('Left').text),
                    int(ctrl_element.find('Top').text))
            elif ctrl_element.tag == 'MainForm':
                #setup background, etc
                cpv_width = int(ctrl_element.find('Width').text)
                cpv_height = int(ctrl_element.find('Height').text)
                cpv_img = self.get_path(ctrl_element.find('BGImage').text)
                if ctrl_element.find('BackColor') is not None:
                    cpv_bg_col = gtk.gdk.color_parse(self.get_colour(abs(int(ctrl_element.find('BackColor').text))))
                    self.winCPViewer.modify_bg(gtk.STATE_NORMAL, cpv_bg_col)
                #position cpviewer
                main_width, main_height = self.WinMain.winMain.get_size_request()
                self.WinMain.fixd.move(self.winCPViewer,
                    ((main_width - cpv_width) / 2),
                    ((main_height - cpv_height) / 2))
                self.winCPViewer.set_size_request(cpv_width, cpv_height)
                self.imgBackground.set_size_request(cpv_width, cpv_height)
                if not os.path.dirname(cpv_img):
                    #if no dir specified, check for image in cpviewer layout dir
                    cpv_img = os.path.join(os.path.dirname(xml_filename), cpv_img)
                if os.path.isfile(cpv_img):
                    self.imgBackground.set_from_file(cpv_img)
        #done
        ctrl_element.clear()

    def get_controls_ini(self, controls_file):
        """load controls.ini file"""
        ctrls_ini = ConfigParser.SafeConfigParser()
        if os.path.isfile(controls_file):
            try:
                ctrls_ini.read(controls_file)
            except ConfigParser.MissingSectionHeaderError:
                self.WinMain.log_msg("Error: Invalid controls.ini file: [%s]" % (controls_file))
                ctrls_ini = None
        return ctrls_ini

    def display_game_details(self, rom_name):
        """pop game details"""
        if not self.cpviewer_ok:
            return
        rom_name = rom_name.lower()
        #for each child
        for evb in self.winCPViewer.get_children():
            if evb.get_name() in _items:
                lbl = evb.child
                #get list of possible control.ini items via widget name
                for ctrl_item in _ctrls_map[evb.get_name()]:
                    if self.ctrls_ini.has_option(rom_name, ctrl_item):
                        #set label text
                        lbl_text = self.ctrls_ini.get(rom_name, ctrl_item)
                        if evb.get_name() == 'GameName':
                            lbl_text = lbl_text.split('(')[0]
                        elif evb.get_name() == 'NumPlayers':
                            if lbl_text == '1':
                                players = 'player'
                            else:
                                players = 'players'
                            lbl_text = '%s %s' % (lbl_text, players)
                        elif evb.get_name() in ['P1JoyType', 'P2JoyType']:
                            lbl_text = lbl_text.split('+')[0]
                        #if len(lbl.get_text()) > 0:
                        #    lbl_text = '%s / %s' % (lbl.get_text(), lbl_text)
                        lbl.set_text(lbl_text)
                        #break
                    else:
                        if evb.get_name() == 'GameName':
                            lbl.set_text(rom_name)
                        else:
                            lbl.set_text('')
        #done - show window
        self.WinMain.show_window('cpviewer')

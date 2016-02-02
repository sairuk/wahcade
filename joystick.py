# -*- coding: UTF-8 -*-
#
###
# Application: wah!cade
# File:        joystick.py
# Description: Wah!Cade Joystick Class
# Copyright (c) 2007,2010   zerodiv, sairuk
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
from wc_common import WahCade
wc = WahCade()

import gtk
_ = gettext.gettext
pygame_imported = False
try:
    import pygame
    pygame_imported = True
except ImportError:
    print _('Warning: pygame module not found.  Joysticks not supported')


class joystick:
    """pygame joystick class"""

    def __init__(self, debug=False):
        """initialise"""
        self.debug = debug
        self.state = {}
        self.devices = {}
        self.ctrls = {}
        self.mw_key_events = []
        self_devices_id = []
        if pygame_imported:
            pygame.init()
            pygame.mixer.quit()
            self.prtjoy = 0
            if debug:
                wc.log_msg("[PYGAME] init ok",1)
 
    # stop and start the joystick            
    def joy_count(self, type):
        pygame.joystick.quit()
        pygame.joystick.init()
        self.num_joysticks = pygame.joystick.get_count()
        for dev_num in range(0, self.num_joysticks):
            if dev_num < self.num_joysticks:
                self.devices[dev_num] = pygame.joystick.Joystick(dev_num)
                if type == 'start':
                    self.devices[dev_num].init()
                    if self.devices[dev_num].get_init:
                        wc.log_msg("[PYGAME] started joystick device with id:%s,  %s" % (self.devices[dev_num].get_id(),self.devices[dev_num].get_name()))
                    else:
                        wc.log_msg("[PYGAME] Joystick device number: %s failed to initialise correctly" % str(dev_num))
                elif type == 'stop':
                    self.devices[dev_num].quit()
                    if self.devices[dev_num].get_init:
                        wc.log_msg("[PYGAME] Stopped joystick device number: %s" % str(dev_num))
                    else:
                        wc.log_msg("[PYGAME] Could not stop device number: %s" % str(dev_num))
                else:
                    return 1
        
    def use_ini_controls(self, ctrlr_ini):
        """read controller ini file"""
        if not pygame_imported:
            return
        for mw_keys in ctrlr_ini.ini_dict.itervalues():
            mw_keys = mw_keys.strip(' "').split(' | ')
            for mw_key in mw_keys:
                if mw_key[:3] == "JOY":
                    self.state[mw_key] = 0
                    (dev_num, control) = mw_key.split("_", 1)
                    dev_num = dev_num[3:]
                    self.devices[int(dev_num) - 1] = None
        self.joy_count('start')

    def use_all_controls(self):
        """which joysticks"""
        if not pygame_imported:
            return
        self.joy_count('start')
        for dev_num in range(0, self.num_joysticks):
            num_buttons = self.devices[dev_num].get_numbuttons()
            for button_num in range(num_buttons):
                mw_key = "JOY%s_BUTTON%s" % (dev_num + 1, button_num)
                ctrl_name = _('Joystick %s Button %s') % (
                    dev_num + 1, button_num)
                self.state[mw_key] = 0
                self.ctrls[ctrl_name] = mw_key
            if self.devices[dev_num].get_numaxes() > 2:
                mw_key = "JOY%s_" % (dev_num + 1)
                ctrl_name = _('Joystick %s ') % (dev_num + 1)
                self.state[mw_key + "UP"] = 0
                self.state[mw_key + "DOWN"] = 0
                self.state[mw_key + "LEFT"] = 0
                self.state[mw_key + "RIGHT"] = 0
                self.ctrls[ctrl_name + _('Up')] = mw_key + "UP"
                self.ctrls[ctrl_name + _('Down')] = mw_key + "DOWN"
                self.ctrls[ctrl_name + _('Left')] = mw_key + "LEFT"
                self.ctrls[ctrl_name + _('Right')] = mw_key + "RIGHT"
    
    # Get the number of joysticks attached to the system
    # Log joystick names
    # Log joystick device numbers    
    def joy_info(self):
        """gather joystick information"""
        for i in range(0, self.num_joysticks):
            wc.log_msg("[PYGAME] Joystick: %s" % str(pygame.joystick.Joystick(i).get_name()))
            wc.log_msg("[PYGAME] Device ID: %s" % str(pygame.joystick.Joystick(i).get_id()))
            wc.log_msg("[PYGAME] Number of axes: %s" % str(pygame.joystick.Joystick(i).get_numaxes()))
            wc.log_msg("[PYGAME] Number of trackballs: %s" % str(pygame.joystick.Joystick(i).get_numballs()))
            wc.log_msg("[PYGAME] Number of buttons: %s" % str(pygame.joystick.Joystick(i).get_numbuttons()))
            wc.log_msg("[PYGAME] Number of hats: %s" % str(pygame.joystick.Joystick(i).get_numhats()))
 
 
    def proc_keys(self, active_window, e, mw_key):
        if active_window.window:
            e.window = active_window.window
            if self.debug:
                wc.log_msg("[PYGAME] joystick, key-release: " + mw_key,1)
                    
    # poll joysticks
    def poll(self, event_cb, initial_repeat_delay=10):
        """poll for joystick events"""
        if not pygame_imported:
            if self.debug:
                wc.log_msg("[PYGAME] not imported, returning from poll function",1)
            return 0
        repeat_delay = 1
        # end polling if no joysticks are found
        self.joy_count('start')
        if self.num_joysticks == 0 and self.prtjoy == 0:
            wc.log_msg("[PYGAME] No joysticks found")
            self.prtjoy = 1
            return 0
        else:
            # give pygame a chance to do its magic with the joystick
            pygame.event.pump()
            # get the focused window or return
            active_window = None
            windows = gtk.window_list_toplevels()
            for window in windows:
                    if window.is_active():
                        active_window = window
                    if active_window == None:
                        return 1
            # check if any of our defined controls were pressed
            mw_key_events = []
            for mw_key in self.state.iterkeys():
                (dev_num, joy_type) = (mw_key.split("_", 1))
                dev_num = int(dev_num[3:]) - 1
                # if binding is for an unfound joystick, continue to next binding
                if dev_num > self.num_joysticks - 1:
                    continue
                if joy_type[:6] == "BUTTON":
                    button_num = joy_type[6:]
                    if self.devices[dev_num].get_button(int(button_num)):
                        self.state[mw_key] += 1
                        mw_key_events.append(mw_key)
                    elif self.state[mw_key] > 0:
                        self.state[mw_key] = 0
                        mw_key_events.append(mw_key)
                    else:
                        if self.debug:
                          wc.log_msg("[PYGAME] Button Not Found %s" % self.devices[dev_num].get_button(int(button_num)))
                        else:
                          pass
                elif joy_type in ["LEFT", "RIGHT", "UP", "DOWN"]:
                    if joy_type in ["LEFT", "RIGHT"]:
                        axis_num = 0
                    else:
                        axis_num = 1
                    axis_value = self.devices[dev_num].get_axis(axis_num)
                    if joy_type in ["UP", "LEFT"]:
                        if axis_value < -0.5:
                            self.state[mw_key] += 1
                            mw_key_events.append(mw_key)
                        elif self.state[mw_key] > 0:
                            self.state[mw_key] = 0
                            mw_key_events.append(mw_key)
                        else:
                            if self.debug:
                              wc.log_msg("[PYGAME] Axis in UP/LEFT Error %s" % self.devices[dev_num].get_axis(axis_num))
                            else:
                              pass
                    else:
                        if axis_value > 0.5:
                            self.state[mw_key] += 1
                            mw_key_events.append(mw_key)
                        elif self.state[mw_key] > 0:
                            self.state[mw_key] = 0
                            mw_key_events.append(mw_key)
                        else:
                            if self.debug:
                              wc.log_msg("[PYGAME] Axis OTHER Error %s" % self.devices[dev_num].get_axis(axis_num))  
                            else:
                              pass
                else:
                    if self.debug:
                      wc.log_msg("[PYGAME] Undefined %s" % joy_type)
                    else:
                      pass
            # send fake key-press events
            if len(mw_key_events) > 0:
                mw_key = mw_key_events[0]
                if self.state[mw_key] == 0:
                    e = gtk.gdk.Event(gtk.gdk.KEY_RELEASE)
                    self.proc_keys(active_window, e, mw_key)
                    event_cb(active_window, e, "JOYSTICK", mw_key)
                elif self.state[mw_key] == 1:
                    e = gtk.gdk.Event(gtk.gdk.KEY_PRESS)
                    self.proc_keys(active_window, e, mw_key)
                    event_cb(active_window, e, "JOYSTICK", mw_key)
            #try clearing event queue
            try:
                pygame.event.clear()
                if self.debug:
                    wc.log_msg("[PYGAME] Cleared pygame events",1)
            except:
                if self.debug:
                    wc.log_msg("[PYGAME] Could not clear PyGame event queue",1)
            return 1

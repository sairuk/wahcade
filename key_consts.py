# -*- coding: utf-8 -*-
#
###
# Application: wah!cade
# File:        key_consts.py
# Description: keyboard constants file
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

mamewah_keys = {
    #numbers
    '0': ['DIK_0'],
    '1': ['DIK_1'],
    '2': ['DIK_2'],
    '3': ['DIK_3'],
    '4': ['DIK_4'],
    '5': ['DIK_5'],
    '6': ['DIK_6'],
    '7': ['DIK_7'],
    '8': ['DIK_8'],
    '9': ['DIK_9'],

    #letters
    'a': ['DIK_A'],
    'b': ['DIK_B'],
    'c': ['DIK_C'],
    'd': ['DIK_D'],
    'e': ['DIK_E'],
    'f': ['DIK_F'],
    'g': ['DIK_G'],
    'h': ['DIK_H'],
    'i': ['DIK_I'],
    'j': ['DIK_J'],
    'k': ['DIK_K'],
    'l': ['DIK_L'],
    'm': ['DIK_M'],
    'n': ['DIK_N'],
    'o': ['DIK_O'],
    'p': ['DIK_P'],
    'q': ['DIK_Q'],
    'r': ['DIK_R'],
    's': ['DIK_S'],
    't': ['DIK_T'],
    'u': ['DIK_U'],
    'v': ['DIK_V'],
    'w': ['DIK_W'],
    'x': ['DIK_X'],
    'y': ['DIK_Y'],
    'z': ['DIK_Z'],

    #cursor keys
    'up': ['DIK_UP', 'DIK_UPARROW'],
    'down': ['DIK_DOWN', 'DIK_DOWNARROW'],
    'left': ['DIK_LEFT', 'DIK_LEFTARROW'],
    'right': ['DIK_RIGHT', 'DIK_RIGHTARROW'],

    #other
    'return': ['DIK_RETURN', 'DIK_NUMPADENTER'],
    'backspace': ['DIK_BACKSPACE', 'DIK_BACK'],
    'tab': ['DIK_TAB'],
    'insert': ['DIK_INSERT'],
    'home': ['DIK_HOME'],
    'page_up': ['DIK_PGUP', 'DIK_PRIOR'],
    'page_down': ['DIK_PGDN', 'DIK_NEXT'],
    'delete': ['DIK_DELETE'],
    'end': ['DIK_END'],
    'pause': ['DIK_PAUSE'],

    #function keys
    'f1': ['DIK_F1'],
    'f2': ['DIK_F2'],
    'f3': ['DIK_F3'],
    'f4': ['DIK_F4'],
    'f5': ['DIK_F5'],
    'f6': ['DIK_F6'],
    'f7': ['DIK_F7'],
    'f8': ['DIK_F8'],
    'f9': ['DIK_F9'],
    'f10': ['DIK_F10'],
    'f11': ['DIK_F11'],
    'f12': ['DIK_F12'],
    'f13': ['DIK_F13'],
    'f14': ['DIK_F14'],
    'f15': ['DIK_F15'],

    #numeric keypad
    'kp_0': ['DIK_NUMPAD0'],
    'kp_1': ['DIK_NUMPAD1'],
    'kp_2': ['DIK_NUMPAD2'],
    'kp_3': ['DIK_NUMPAD3'],
    'kp_4': ['DIK_NUMPAD4'],
    'kp_5': ['DIK_NUMPAD5'],
    'kp_6': ['DIK_NUMPAD6'],
    'kp_7': ['DIK_NUMPAD7'],
    'kp_8': ['DIK_NUMPAD8'],
    'kp_9': ['DIK_NUMPAD9'],
    'kp_down': ['DIK_NUMPAD2'],
    'kp_up': ['DIK_NUMPAD8'],
    'kp_left': ['DIK_NUMPAD4'],
    'kp_right': ['DIK_NUMPAD6'],
    'kp_divide': ['DIK_NUMPADSLASH', 'DIK_DIVIDE'],
    'kp_multiply': ['DIK_NUMPADSTAR', 'DIK_MULTIPLY'],
    'kp_subtract': ['DIK_NUMPADMINUS', 'DIK_SUBTRACT'],
    'kp_add': ['DIK_NUMPADPLUS', 'DIK_ADD'],
    'kp_decimal': ['DIK_NUMPADPERIOD', 'DIK_DECIMAL'],
    'kp_enter': ['DIK_NUMPADENTER'],

    #punctuation
    'grave': ['DIK_GRAVE'],
    'backslash': ['DIK_BACKSLASH'],
    'minus': ['DIK_MINUS'],
    'equal': ['DIK_EQUALS', 'DIK_NUMPADEQUALS'],
    'bracketleft': ['DIK_LBRACKET'],
    'bracketright': ['DIK_RBRACKET'],
    'semicolon': ['DIK_SEMICOLON'],
    'apostrophe': ['DIK_APOSTROPHE'],
    'comma': ['DIK_COMMA', 'DIK_NUMPADCOMMA'],
    'period': ['DIK_PERIOD'],
    'slash': ['DIK_SLASH'],
    'space': ['DIK_SPACE'],

    #modifier keys
    'escape': ['DIK_ESCAPE'],
    'shift_l': ['DIK_LSHIFT'],
    'shift_r': ['DIK_RSHIFT'],
    'control_l': ['DIK_LCONTROL'],
    'control_r': ['DIK_RCONTROL'],
    'meta_l': ['DIK_LWIN'],
    'meta_r': ['DIK_RWIN'],
    'alt_l': ['DIK_LALT', 'DIK_LMENU'],
    'alt_r': ['DIK_RALT'],
    'menu': ['DIK_RMENU'],
    'caps_lock': ['DIK_CAPSLOCK'],
    'num_lock': ['DIK_NUMLOCK'],
    'scroll_lock': ['DIK_SCROLL'],

    #keys not recognized in GTK
    'voidsymbol': ['DIK_CAPITOL'],
    'unknown': ['DIK_APPS'],
    'unknown': ['DIK_SYSRQ']}

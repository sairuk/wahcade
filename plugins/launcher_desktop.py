#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
###
# Application: sc_desktop
# File:        sc_desktop.py
# Description: .desktop shortcut plugin
# Copyright (c) 2005-2012   Wayne Moulden <http://www.mameau.com>
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
# CHANGELOG
# 2013-11-04
#  Added handling of quoted string
#  Return True to skip executable check
#
# EXAMPLE FILE
#============================================================
# [Desktop Entry]
# Version=1.0
# Type=Application
# Terminal=false
# Icon[en_AU]=/usr/local/share/wahcade/pixmaps/wahcade.png
# Name[en_AU]=Wah!Cade
# Exec=/usr/bin/wahcade
# Name=Wah!Cade
# Icon=/usr/local/share/wahcade/pixmaps/wahcade-logo.png

import os, sys, subprocess
from subprocess import Popen

"""Plugin for Mah!Cade"""
def __init__(scfile=""):
    if (len(sys.argv) > 1):
        scfile = sys.argv[1]
    if (len(scfile) > 1):
        result = read_scexec(scfile) 
        if (len(result[0]) > 1): 
            run_scexec(result[0],result[1])
        else:
            return result[3]          
    else:
        return "No shortcut file passed"        

def read_scexec(scfile):
    """ read shortcut and return executable path """
    skip_check = False
    if sys.platform != 'win32':
        f = open(scfile.replace('\"',''))
        for line in f:
            if line[:5] == "Exec=":
                cmd = line[5:]
                return  "Executing " + cmd, cmd, "", "", True, True
        return "Ran into problems finding executable in .desktop shortcut"
    else:
        return "Only available for non-windows platforms! returning" 
    
def run_scexec(cmd, args, work_dir, message=""):
    if work_dir:
        os.chdir(os.path.join(os.path.abspath(sys.path[0]), work_dir))
    else:
        os.chdir(os.path.split(cmd)[0])
    if args:
        cmd = cmd + " " + args
    p = subprocess.Popen(cmd, shell=True)
    p.wait

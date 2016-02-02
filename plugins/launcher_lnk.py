#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
###
# Application: sc_lnk
# File:        sc_lnk.py
# Description: .lnk shortcut plugin
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
###
#
# Created with guidance from 
# http://timgolden.me.uk/python/win32_how_do_i/create-a-shortcut.html 

import os, sys, subprocess
from subprocess import Popen

"""Plugin for Mah!Cade"""
def __init__():
    if (len(sys.argv) > 1):    
        result = read_scexec(sys.argv[1])
        if (len(result[0]) > 1): 
            run_scexec(result[0],result[1])
        else:
            return result[3]
    else:
        return "No shortcut file passed"        
    
def read_scexec(scfile):
    """ read shortcut and return executable path """
    if sys.platform != 'win32':
        return "Only available for windows platforms! returning"
    try:
        import pythoncom
        from win32com.shell import shell, shellcon
    except:
        return "pythoncom module not found! \n download from http://sourceforge.net/projects/pywin32/files/pywin32/"
    shortcut = pythoncom.CoCreateInstance (
      shell.CLSID_ShellLink,
      None,
      pythoncom.CLSCTX_INPROC_SERVER,
      shell.IID_IShellLink
    )
    shortcut.QueryInterface (pythoncom.IID_IPersistFile).Load (scfile, 0)
    cmd, _ = shortcut.GetPath (shell.SLGP_UNCPRIORITY)
    args = shortcut.GetArguments ()
    work_dir = shortcut.GetWorkingDirectory()    
    return "Executing " + cmd, cmd, args, work_dir, False, False
    
def run_scexec(cmd, args, work_dir, message=""):
    if work_dir:
        os.chdir(os.path.join(os.path.abspath(sys.path[0]), work_dir))
    else:
        os.chdir(os.path.split(cmd)[0])
    if args:
        cmd = cmd + " " + args
    p = subprocess.Popen(cmd, shell=True)
    p.wait
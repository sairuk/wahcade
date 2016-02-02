#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
###
# Application: wah!cade
# File:        mamewah_ini.py
# Description: read mamewah formatted ini file
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
from constants import *


class MameWahIni:

    def __init__(self, ini_filename, ini_type='default', min_version=None):
        """init ini class"""
        self.ini_filename = ini_filename
        self.ini_type = ini_type
        #read file if one had been provided
        if not os.path.exists(ini_filename):
            print "Error: ini file: [%s] does not exist." % (ini_filename)
            sys.exit(1)
        else:
            self.read()
            #check version?
            if min_version:
                all_nums = '0123456789.'
                s = self.lines[0]
                v1 = s[s.find('('):]
                tmp = ''
                try:
                    current_version = tmp.join([c for c in v1 if c in all_nums])
                    if current_version != '':
                        if not self._version_check(min_version, current_version):
                            print "Error: version of ini file: [%s] is: %s.\n  Min version required is: %s" % (
                                ini_filename, current_version, min_version)
                            print "  Get the latest version template from: [%s] directory" % (
                                os.path.join(os.getcwd(), 'config.dist'))
                except:
                    pass

    def _version_check(self, v1, v2):
        """returns true if v1 < v2"""
        l = [(int(x) <= int(y)) for x, y in zip(v1.split('.'), v2.split('.'))]
        for test in l:
            if not test:
                return False
        return True

    def _create_dictionary(self):
        """create a dictionary for future lookups"""
        d = {}
        for line in self.lines:
            if not line.startswith('#') and line != '':
                l = line.split(' ', 1)
                #get key and value
                key = str(l[0]).strip()
                if len(l) > 1:
                    value = str(l[1]).strip()
                else:
                    value = ''
                d[key] = value
        return d

    def read(self):
        """read ini file"""
        self.lines = []
        if os.path.isfile(self.ini_filename):
            self.lines = open(self.ini_filename, 'r').readlines()
            self.lines = [s.strip() for s in self.lines]
            self.lines = [s.replace('\t', ' ') for s in self.lines]
        #create lookup dictionary
        self.ini_dict = self._create_dictionary()

    def write(self):
        """save ini file"""
        #get list of items that aren't in the original file
        original_keys = self._create_dictionary().keys()
        new_keys = self.ini_dict.keys()
        missing_keys = list(set(new_keys) - set(original_keys))
        #update original lines in ini file from dictionary
        for i, line in enumerate(self.lines):
            spc_pos = line.find(' ')
            if spc_pos == -1:
                spc_pos = len(line)
            option = line[:spc_pos]
            if option in self.ini_dict:
                #build line
                self.lines[i] = '%s%s' % (option.ljust(40), self.ini_dict[option])
        #add missing keys
        if missing_keys:
            #print "missing keys=",missing_keys
            self.lines.append('')
            self.lines.append('### Added in v%s "%s" ###' % (VERSION, VERSION_NAME))
            for mk in missing_keys:
                self.lines.append('%s%s' % (mk.ljust(40), self.ini_dict[mk]))
        #add correct line terminator
        lines = ['%s\n' % s for s in self.lines]
        #write file
        open(self.ini_filename, 'w').writelines(lines)

    def has_option(self, option):
        """does the option exist"""
        return option in self.ini_dict

    def get(self, option, get_mode='default', default_value=''):
        """return value for given option"""
        if option in self.ini_dict:
            value = self.ini_dict[option]
            #set default value if none found
            if value == '':
                value = default_value
            #expand path if it exists
            if value != '' and get_mode != 'int':
                test_path = os.path.expanduser(value)
                if os.path.exists(test_path):
                    value = os.path.normcase(test_path)
        else:
            if default_value == '':
                print 'Error: option: [%s] for ini file: [%s] not found' % (option, self.ini_filename)
                value = ''
            else:
                value = default_value
        #done
        return value

    def getint(self, option, default_value=''):
        """return integer value for given option"""
        try:
            int_val = int(self.get(option, 'int', default_value))
        except ValueError:
            int_val = 0
        #done
        return int_val

    def reverse_get(self, value):
        """return possible options for given value"""
        if self.ini_type == 'ctrlr':
            #split keycode values into a list
            d = {}
            for k, v in self.ini_dict.items():
                lv = v.strip(' "').split(' | ')
                d[k] = lv
            #get list of options containing keycode value
            option = [k for k, v in d.items() if value in v]
        else:
            option = [k for k, v in self.ini_dict.items() if value in v]
        #done
        return option

    def set(self, option, value):
        """set option to given value"""
        #if no value, set to empty string
        if value is None:
            value = ''
        elif os.path.exists(str(value)):
            home_path = os.path.normpath(os.path.normcase(os.path.expanduser('~')))
            test_path = value.replace(home_path, '~')
            if os.path.exists(os.path.expanduser(test_path)):
                value = test_path
        self.ini_dict[option] = value

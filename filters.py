#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
###
# Application: wah!cade
# File:        filters.py
# Description: routines to read / write mamewah filters and lists
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
import fnmatch
import codecs
import ConfigParser

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
try:
    from chardet.universaldetector import UniversalDetector
except:
    print 'Warning: could not find python-chardet module'
    print '         this could result in unicode errors'
from constants import *
_ = gettext.gettext
#category

#filter sections
_sections = [
    'filter_type',
    'year',
    'manufacturer',
    'driver',
    'display_type',
    'screen_type',
    'controller_type',
    'driver_status',
    'colour_status',
    'sound_status',
    'category']
#controller types
_controllers = {
    'dial': u'Spinner (or 360\xb0 Wheel)',
    'doublejoy2way': u'Double 2-Way Joysticks',
    'doublejoy4way': u'Double 4-Way Joysticks',
    'doublejoy8way': u'Double 8-Way Joysticks',
    'doublejoy': u'Double Joysticks',
    'doublejoyvertical2way': u'Double 2-Way Vertical Joysticks',
    'gambling': u'Gambling',
    'hanafuda': u'Hanafuda',
    'joy1way': u'1-Way Joystick', 
    'joy2way': u'2-Way Joystick',
    'joy4way': u'4-Way Joystick',
    'joy8way': u'8-Way Joystick',
    'joy': u'Joystick',
    'joyvertical2way': u'2-Way Vertical Joystick',
    'joy3 (half4)way': u'Crazy Named Joystick', 
    'joy5 (half8)way': u'Crazy Named Joystick',
    'doublejoy5 (half8)way': u'Crazy Named Joystick', 
    'keyboard': u'Keyboard',
    'keypad': u'Keypad',
    'lightgun': u'Light-Gun',
    'mahjong': u'Mahjong',
    'mouse': u'Mouse',
    'paddle': u'Paddle (or ~270\xb0 Wheel)',
    'pedal': u'Pedal',
    'positional': u'Positional',
    'stick': u'Analogue Joystick (or ~270\xb0 Wheel)',
    'trackball': u'Trackball',
    'triplejoy': u'Triple Joystick',
    'triplejoy8way': u'Triple 8-Way Joystick',
    'vdoublejoy2way': u'Double Vertical 2-Way Joysticks',
    'vjoy2way': u'Vertical 2-Way Joystick',
    '': u'None'}

def get_file_encoding(filename):
    """autodetects the encoding of the given file"""
    detector = UniversalDetector()
    detector.reset()
    i = 0
    if not os.path.exists(os.path.expanduser(filename)):
        return 'ascii'
    for line in file(filename, 'rb'):
        detector.feed(line)
        i += 1
        #done or hit max lines (it takes ages to read a large file)
        if detector.done or i >= 2000:
            break
    detector.close()
    return detector.result



def open_file(filename, filemode='r'):
    """opens given filename, and autodetects the encoding"""
    #detect encoding
    try:
        file_enc = get_file_encoding(filename)['encoding'] or 'latin'
    except:
        file_enc = sys.getdefaultencoding()
    #use utf8 instead of ascii
    if file_enc.lower() == 'ascii' or file_enc.lower() == 'eur-kr':
        file_enc = 'latin'
    #open file using correct encoding
    f = codecs.open(filename, mode=filemode, encoding=file_enc)
    return f, file_enc


def get_dat_game_item(dat_filename):
    """read dat file"""
    #needs to be an iterator returning next item in file each time
    #f = codecs.open(dat_filename, mode='r', encoding='utf-8')
    f, file_enc = open_file(dat_filename)
    for line in f:
        line = line.strip()
        #look for start of item
        if line == 'game (':
            #setup empty
            d = {'rom_name': '',
                'game_name': '',
                'year': '',
                'manufacturer': '',
                'clone_of': '',
                'rom_of': '',
                'display_type': '',
                'screen_type': '',
                'controller_type': '',
                'driver_status': '',
                'colour_status': '',
                'sound_status': '',
                'category': ''}
            #get item attribs
            while line != ')':
                if line.startswith('\t'):
                    key, value = line.split(' ', 1)
                    value = value.strip('"')
                    if key == '\tname':
                        d['rom_name'] = value
                    elif key == '\tcloneof':
                        d['clone_of'] = value
                    elif key == '\t':
                        d['rom_of'] = value
                    elif key == '\tdescription':
                        d['game_name'] = value
                    elif key == '\tyear':
                        d['year'] = value
                    elif key == '\tmanufacturer':
                        d['manufacturer'] = value
                    elif key == '\tvideo':
                        vid = {}
                        l = value[2:-2].split()
                        for i in range(0, len(l) - 1, 2):
                            vid[l[i]] = l[i+1]
                        if 'screen' in vid:
                            d['display_type'] = vid['screen']
                        if 'orientation' in vid:
                            d['screen_type'] = vid['orientation']
                    elif key == '\tdriver':
                        driver = {}
                        l = value[2:-2].split()
                        for i in range(0, len(l) - 1, 2):
                            driver[l[i]] = l[i+1]
                        if 'status' in driver:
                            d['driver_status'] = driver['status']
                        if 'color' in driver:
                            d['colour_status'] = driver['color']
                        if 'sound' in driver:
                            d['sound_status'] = driver['sound']
                    elif key == '\tinput':
                        ctrl = {}
                        l = value[2:-2].split()
                        for i in range(0, len(l) - 1, 2):
                            ctrl[l[i]] = l[i+1]
                        if 'control' in ctrl:
                            d['controller_type'] = _controllers[ctrl['control']]
                    #get category
                    if driver is not None:
                        d['category'] = get_catver_item(d['rom_name'].lower())
                #read next time
                line = f.next()
                line = line.strip('\n')
            #yield back to calling fund
            yield d
    #done
    f.close()


def get_xml_game_item(xml_filename):
    """get game bits"""
    #mame version
    #mame_version = '0'
    for event, mame_element in ET.iterparse(xml_filename, events=('start', 'end')):
        #get mame version element
        print mame_element.tag
        if mame_element.tag == 'mame' or mame_element.tag == 'mess' or mame_element.tag == 'softwarelist':
            #or mame_element.tag == 'softwarelists' 
            if 'build' not in mame_element.attrib:
                mame_version = '0.000'
            else:
                spc_pos = mame_element.attrib['build'].find(' ')
                if spc_pos == -1:
                    spc_pos = len(mame_element.attrib['build'])
                mame_version = mame_element.attrib['build'][:spc_pos]
            mame_element.clear()
            break
    #games
    for event, game_element in ET.iterparse(xml_filename):
        #for each game
        if game_element.tag == 'game' or game_element.tag == 'machine' or game_element.tag == 'software':
            d = {'rom_name': '',
                'game_name': '',
                'year': '',
                'manufacturer': '',
                'clone_of': '',
                'rom_of': '',
                'display_type': '',
                'screen_type': '',
                'controller_type': '',
                'driver_status': '',
                'colour_status': '',
                'sound_status': '',
                'category': ''}
            #get sub elements
            if mame_version > '0.106':
                vid = game_element.find('display')
                input_ctrl = game_element.find('input')
                if input_ctrl is not None:
                    ctrl = input_ctrl.find('control')
            else:
                vid = game_element.find('video')
                ctrl = game_element.find('input')
            driver = game_element.find('driver')
            year = game_element.findtext('year') or ''
            manu = game_element.findtext('manufacturer') or '' or game_element.findtext('publisher')
            if manu == "<unknown>" or manu == "<Unknown>" or manu == None  : # Make <unknown> tag in mess software lists look nice
                manu = "Unknown"
            if manu == "<Generic>" or manu == "<generic>": # Make <generic> tag in mess software lists look nice
                manu = "Generic" 
            desc = game_element.findtext('description') or ''
            #create dict
            d['rom_name'] = game_element.attrib['name']#.upper()
            d['game_name'] = desc
            d['year'] = year
            d['manufacturer'] = manu.title()
            if 'cloneof' in game_element.keys():
                d['clone_of'] = game_element.attrib['cloneof']#.upper()
            if 'romof' in game_element.keys():
                d['rom_of'] = game_element.attrib['romof']#.upper()
            if vid is not None:
                if mame_version > '0.106':
                    d['display_type'] = vid.attrib['type'].title()
                    d['screen_type'] = vid.attrib['rotate'].title()
                else:
                    d['display_type'] = vid.attrib['screen'].title()
                    d['screen_type'] = vid.attrib['orientation'].title()
            if ctrl is not None:
                ctrl_unk = False
                if mame_version > '0.106':
                    if 'ways' in ctrl.keys() and 'type' in ctrl.keys():
                        ctrlkey = "%s%sway" % (ctrl.attrib['type'],ctrl.attrib['ways'])                                                                                                      
                    elif 'type' in ctrl.keys():
                        ctrlkey = ctrl.attrib['type']
                    else:
                        ctrl_unk = True
                else:
                    if 'control' in ctrl.keys():
                        ctrlkey = ctrl.attrib['control']
                    else:
                        ctrl_unk = True
                # Game has no controller type listed
                if ctrl_unk:
                    d['controller_type'] = 'Unknown'
                    ctrl_unk = False
                else:
                    # Game has controller type listed, check for existence of key
                    if ctrlkey in _controllers:
                      d['controller_type'] = _controllers[ctrlkey] 
                    else:
                      print "WARNING: %s is not in our known controllers types, please report (https://bugs.launchpad.net/wahcade)." % ctrlkey
                      d['controller_type'] = 'Unknown'
            if driver is not None:
                d['driver_status'] = 'Status %s' % (driver.attrib['status'].title())
                d['colour_status'] = 'Color %s' % (driver.attrib['color'].title())
                d['sound_status'] = 'Sound %s' % (driver.attrib['sound'].title())
                d['category'] = get_catver_item(d['rom_name'].lower())
            yield d
    game_element.clear() # won't need this any more


def get_catver_item(rom_name):
    #get category info  
    try:
        category = catverparser.get('Category', rom_name).decode(_catenc['encoding'], "ignore")
    except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
        category = 'Unknown'
    return category


def create_initial_filter(info_filename, filter_filename, list_filename, emu_ini, pgb_pulse=None):
    """create a new mamewah .ftr & .lst file"""
    global catverparser, _catenc
    pulse_cnt = 0
    #catver = get_catver_ini(_catver_ini)
    catverparser = ConfigParser.SafeConfigParser()
    catverparser.read(_catver_ini)
    if _catver_ini:
        _catenc = get_file_encoding(_catver_ini)
    #create empty dict
    mwfilter = {}
    for s in _sections[1:]:
        mwfilter[s] = []
    #open new list file
    f, file_enc = open_file(list_filename, 'w')
    #get rom path & ext, etc
    rom_path = emu_ini.get('rom_path')
    if not os.path.exists(rom_path):
        print _('Error: rom path: [%s] does not exist' % (rom_path))
    rom_ext = emu_ini.get('rom_extension')
    rom_list_gen = 'rom_folder' in emu_ini.get('list_generation_method')
    #nms file?
    nms_entries = read_nms_file(emu_ini.get('nms_file'))    
    #method?
    if emu_ini.get('list_generation_method') == 'rom_folder':
        #just rom folder, so create a basic lst fileD
        #roms = glob.glob(os.path.join(rom_path, '*%s' % (rom_ext)))
        roms = walk_dir(rom_path, False, rom_ext, False)
        if roms is None:
            print "Error, no files found during walk_dir"
            return
        roms.sort() 
        gd = {'rom_name': '',
            'game_name': '',
            'year': '',
            'manufacturer': '',
            'clone_of': '',
            'rom_of': '',
            'display_type': '',
            'screen_type': '',
            'controller_type': '',
            'driver_status': '',
            'colour_status': '',
            'sound_status': '',
            'category': ''}
        for rom_filename in roms:
            rom_name = os.path.splitext(os.path.basename(rom_filename))[0]
            if rom_name in nms_entries:
                game_name = nms_entries[rom_name]
            else:
                game_name = rom_name
            #set rom & game name
            gd['rom_name'] = rom_name
            gd['game_name'] = game_name
            ###### LOOK UP CATEGORY HERE
            gd['category'] = get_catver_item(gd['rom_name']).lower()
            add_game_to_filtered_list(gd, f)
        f.close()
        return
    #check info file
    if os.path.exists(info_filename):
        #create iterator for game info
        r, ext = os.path.splitext(info_filename)
        if ext == '.xml':
            mi = get_xml_game_item(info_filename)
        else:
            mi = get_dat_game_item(info_filename)
    elif emu_ini.get('list_generation_method') != 'rom_folder':
        #file not found
        print _     ('Error: emulator info file: [%s] does not exist' % (info_filename))
        print _('       cannot create initial filters!')
        mi = None
        f.close()
        return
    #use dat / xml info iterator
    while True:
        try:
            #get details of next rom
            gd = mi.next()
            #pulse progress bar?
            pulse_cnt += 1
            if pgb_pulse and pulse_cnt > 10:
                pulse_cnt = 0
                pgb_pulse()
            #write gd to list file
            try:
                #check rom actually exists in rom folder location?
                add_game = True
                if rom_list_gen:
                    #check using lowercase rom name
                    rom_filename = os.path.join(rom_path, '%s.%s' % (gd['rom_name'].lower(), rom_ext))
                    if not os.path.isfile(rom_filename):
                        #check using uppercase rom name
                        rom_filename = os.path.join(rom_path, '%s.%s' % (gd['rom_name'].upper(), rom_ext))
                        if not os.path.isfile(rom_filename):
                            #rom file doesn't exist, so don't add
                            add_game = False
                #unicode name
                gd['rom_name'] = gd['rom_name'].encode('latin','ignore')
                gd['game_name'] = gd['game_name'].encode('latin','ignore')
                #add game to list?
                if add_game:
                    add_game_to_filtered_list(gd, f)
            except TypeError, msg:
                print '  game dictionary=', gd
                sys.exit(1)
        except StopIteration:
            break
        #for each key in sections
        for k in _sections[1:]:
            if k in gd:
                if gd[k] not in mwfilter[k]:
                    mwfilter[k].append(gd[k])
    #done list file
    f.close()
    #write filter file
    wrtFilterFile(filter_filename,mwfilter)


def read_filter(filter_file):
    """read a mamewah .ftr file"""
    #init
    gap_num = 0
    d = {}
    l=[]
    #open file
    try:
        f, filenc = open_file(filter_file, 'r')
    except IOError:
        print _('Error: filter file: [%s] does not exist' % (filter_file))
        return {}
    #get type
    try:
        line = f.next()
        line = line.strip()
        d[_sections[0]] = line
        f.next()
    except StopIteration:
        #filter file too short
        print _('Error: filter file: [%s] invalid (too short!)' % (filter_file))
        #print _('
        return {}
    #for each line in file
    for line in f:
        line = line.strip()
        if line == '':
            #end of section, add current list (as a dictionary) to filter
            gap_num += 1
            d[_sections[gap_num]] = dict(l)
            l = []
        else:
            #read name & true / false setting
            try:
                next_line = f.next().strip()
            except StopIterator:
                next_line = 'False'
            filt_item = [line, next_line.lower() == 'true']
            l.append(filt_item)
    #done, close file & return dictionary
    f.close()
    return d


def write_filter(filter_spec, filter_filename):
    """write a filter file from a given spec"""
    f, file_enc = open_file(filter_filename, 'w')
    #write filter type
    f.write('%s\n\n' % filter_spec[_sections[0]])
    #write other sections
    for key in _sections[1:]:
        l = filter_spec[key].items()
        l.sort()
        for item, value in l:
            f.write('%s\n%s\n' % (item, str(value)))
        f.write('\n')
    #done
    f.close()


def create_filtered_list(original_list_filename, filter_spec, list_filename):
    """create a mamewah .lst file from <emu>-0.lst and the given spec"""
    #open empty list file
    f, file_enc = open_file(list_filename, 'w')
    #get all games
    all_games, len_all_games = read_filtered_list(original_list_filename)
    all_games_roms = [l[1] for l in all_games]
    #for each item in iterator
    for game_item in all_games:
        gd = get_game_dict(game_item)
        #match filter conditions
        matched = True
        #check filter type section
        if int(filter_spec['filter_type']) != FTR_CLONES_YES and gd['clone_of'] != '':
            matched = False
        if (int(filter_spec['filter_type']) == FTR_CLONES_BETTER and
              gd['clone_of'] != '' and
              'good' in gd['driver_status'].lower()):
            #see if original's driver status is worse than this one
            try:
                orig_rom = get_game_dict(all_games[all_games_roms.index(gd['clone_of'])])
            except ValueError:
                #print _("Warning: can't find parent rom: [%s] for clone: [%s]") % (gd['clone_of'], gd['rom_name'])
                matched = True
            if 'good' not in orig_rom['driver_status'].lower():
                matched = True
        #check the other sections
        if matched:
            #for each section
            for section in _sections[1:]:
                if section in filter_spec and section in gd:
                    #if spec and current game have same section
                    if gd[section] in filter_spec[section]:
                        if not filter_spec[section][gd[section]]:
                            #don't match if spec entry for game not set (i.e. False)
                            matched = False
        if matched:
            #write output
            add_game_to_filtered_list(gd, f)
    #done, close file
    f.close()


def read_filtered_list(list_filename):
    """read a mamewah .lst file"""
    l = []
    #create an empty file if necessary
    if not os.path.isfile(list_filename):
        f, file_enc = open_file(list_filename, 'w')
        f.close()
    #open file
    f, file_enc = open_file(list_filename, 'r')
    lines = f.readlines()
    f.close()
    lines = [s.strip() for s in lines]
    #for each game...
    if len(lines) % 13 <> 0:
        print _     ('Warning: list file: [%s] format is invalid' % (list_filename))
        print _('       Loading partial list...')
        return 1, 1
    else:
        for i in range(0, len(lines), 13):
            item = []
            for j in range(13):
                item.append(lines[i + j])
            #reverse first two columns
            item2 = [item[1], item[0]]
            item2.extend(item[2:])
            l.append(item2)
        #done
        return l, len(l)


def add_game_to_filtered_list(gd, file_obj=None, list_filename=None):
    """add game info in given dictionary to specified file or .lst file"""
    if list_filename is not None:
        #open file for appending if necessary
        file_obj, file_enc = open_file(list_filename, 'a')
    #write dictionary to file
    file_obj.writelines([
        '%s\n' % gd['rom_name'],
        '%s\n' % gd['game_name'],
        '%s\n' % gd['year'],
        '%s\n' % gd['manufacturer'],
        '%s\n' % gd['clone_of'],
        '%s\n' % gd['rom_of'],
        '%s\n' % gd['display_type'],
        '%s\n' % gd['screen_type'],
        '%s\n' % gd['controller_type'],
        '%s\n' % gd['driver_status'],
        '%s\n' % gd['colour_status'],
        '%s\n' % gd['sound_status'],
        '%s\n' % str(gd['category'])])
    #done
    if list_filename is not None:
        file_obj.close()


def write_filtered_list(list_filename, list_items):
    """write the given list items into the specified .lst file"""
    #f= codecs.open(list_filename, mode='w', encoding='utf-8')
    f, file_enc = open_file(list_filename, 'w')
    for game_info in list_items:
        f.writelines([
            '%s\n' % game_info[GL_ROM_NAME],
            '%s\n' % game_info[GL_GAME_NAME],
            '%s\n' % game_info[GL_YEAR],
            '%s\n' % game_info[GL_MANUFACTURER],
            '%s\n' % game_info[GL_CLONE_OF],
            '%s\n' % game_info[GL_ROM_OF],
            '%s\n' % game_info[GL_DISPLAY_TYPE],
            '%s\n' % game_info[GL_SCREEN_TYPE],
            '%s\n' % game_info[GL_CONTROLLER_TYPE],
            '%s\n' % game_info[GL_DRIVER_STATUS],
            '%s\n' % game_info[GL_COLOUR_STATUS],
            '%s\n' % game_info[GL_SOUND_STATUS],
            '%s\n' % game_info[GL_CATEGORY]])
    #done
    f.close()


def read_fav_list(favlist_filename):
    """reads a .fav list"""
    d = {}
    f, file_enc = open_file(favlist_filename, 'r')
    lines = f.readlines()
    f.close()
    lines = [s.strip() for s in lines]
    #for each game...
    for i in range(0, len(lines), 4):
        item = []
        for j in range(4):
            item.append(lines[i + j])
        #add to favs dictionary
        d[item[FAV_ROM_NAME]] = [
            item[FAV_ROM_NAME],
            item[FAV_GAME_NAME],
            int(item[FAV_TIMES_PLAYED]),
            int(item[FAV_MINS_PLAYED])]
    #done
    return d


def write_fav_list(favlist_filename, favs):
    """writes a .fav list"""
    f, file_enc = open_file(favlist_filename, 'w')
    for fav_key in favs.keys():
        f.writelines([
            '%s\n' % fav_key,
            '%s\n' % favs[fav_key][FAV_GAME_NAME],
            '%s\n' % favs[fav_key][FAV_TIMES_PLAYED],
            '%s\n' % favs[fav_key][FAV_MINS_PLAYED]])
    f.close()


def get_game_dict(game_item):
    """return dictionary of info for given game item"""
    gd = {
        'rom_name': game_item[GL_ROM_NAME],
        'game_name': game_item[GL_GAME_NAME],
        'year': game_item[GL_YEAR],
        'manufacturer': game_item[GL_MANUFACTURER],
        'clone_of': game_item[GL_CLONE_OF],
        'rom_of': game_item[GL_ROM_OF],
        'display_type': game_item[GL_DISPLAY_TYPE],
        'screen_type': game_item[GL_SCREEN_TYPE],
        'controller_type': game_item[GL_CONTROLLER_TYPE],
        'driver_status': game_item[GL_DRIVER_STATUS],
        'colour_status': game_item[GL_COLOUR_STATUS],
        'sound_status': game_item[GL_SOUND_STATUS],
        'category': game_item[GL_CATEGORY]}
    return gd


def read_nms_file(nms_filename):
    """returns a dictionary created from a nms formatted file"""
    d = {}
    if nms_filename == '':
        return d
    #read file
    try:
        f, file_enc = open_file(nms_filename, 'r')
        nms_lines = f.readlines()
        f.close()
    except IOError:
        print _('Error: nms file [%s] does not exist' % (nms_filename))
        return d
    nms_lines = [s.strip() for s in nms_lines]
    #create dictionary
    nms_recs = [l.split('|') for l in nms_lines]
    for r in nms_recs:
        if r != ['']:
            d[r[1]] = r[0]
    #done
    return d


def walk_dir(root, recurse=False, pattern='*', return_folders=False):
    # initialize
    result = []
    # must have at least root folder
    try:
        names = os.listdir(root)
    except os.error:
        return result
    # expand pattern
    pattern = pattern or '*'
    pat_list = pattern.split(';')
    # check each file
    for name in names:
        fullname = os.path.normpath(os.path.join(root, name))
        # grab if it matches our pattern and entry type
        for pat in pat_list:
            if pat == "*":
                pat = '*'
            else:
                pat = '*.%s' % (pat)
            if fnmatch.fnmatch(fullname, pat):
                #if os.path.isfile(fullname) or (return_folders and os.path.isdir(fullname)):
                if return_folders:
                    if os.path.isdir(fullname):
                        result.append(fullname)
                else:
                    if os.path.isfile(fullname):
                        result.append(fullname)
                continue
            else:
                print "Cannot match:", fullname
                continue
        # recursively scan other folders, appending results
        if recurse:
            if os.path.isdir(fullname) and not os.path.islink(fullname):
                result = result + walk_dir(fullname, recurse, pattern, return_folders)
    return result


if __name__ == '__main__':
    import time
    from mamewah_ini import MameWahIni
    #set vars
    cdir = sys.path[0]
    global _catver_ini, _catenc
    _catver_ini = ""
    _catenc = get_file_encoding(_catver_ini)
    #_mameinfo_file = os.path.join(cdir, 'mameinfo111.xml')
    #set to unicode encoding
    try:
        sys.setappdefaultencoding('utf-8')
    except AttributeError:
        pass
    #test nms feed
    #print read_nms_file(os.path.expanduser('~/emulators/pc/pc_games.nms'))


#write filter file
def wrtFilterFile(filter_filename,mwfilter):
    f, file_enc = open_file(filter_filename, 'w')
    f.write('1\n\n')
    for key in _sections[1:]:
        l = mwfilter[key]
        l.sort()
        for item in l:
            if item is not None and item != '':
                try:
                    f.write('%s\nTrue\n' % (item))
                except UnicodeEncodeError, msg:
                    print 'unicode encode error\n  msg=', msg
                except UnicodeDecodeError, msg:
                    print 'unicode decode error\n  msg=', msg
        f.write('\n')
    f.close()
    return
